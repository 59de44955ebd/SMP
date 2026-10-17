#include "player.h"

template <class Q>
HRESULT GetEventObject(IMFMediaEvent *pEvent, Q **ppObject)
{
    *ppObject = NULL;   // zero output

    PROPVARIANT var;
    HRESULT hr = pEvent->GetValue(&var);
    if (SUCCEEDED(hr))
    {
        if (var.vt == VT_UNKNOWN)
        {
            hr = var.punkVal->QueryInterface(ppObject);
        }
        else
        {
            hr = MF_E_INVALIDTYPE;
        }
        PropVariantClear(&var);
    }
    return hr;
}

//######################################
//  Static class method to create the CPlayer object.
//######################################
HRESULT CPlayer::CreateInstance(
    HWND hVideo,                  // Video window.
    HWND hEvent,                  // Window to receive notifications.
    CPlayer **ppPlayer)           // Receives a pointer to the CPlayer object.
{
    if (ppPlayer == NULL)
    {
        return E_POINTER;
    }

    CPlayer *pPlayer = new (std::nothrow) CPlayer(hVideo, hEvent);
    if (pPlayer == NULL)
    {
        return E_OUTOFMEMORY;
    }

    HRESULT hr = pPlayer->Initialize();
    if (SUCCEEDED(hr))
    {
        *ppPlayer = pPlayer;
    }
    else
    {
        pPlayer->Release();
    }
    return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::Initialize()
{
    // Start up Media Foundation platform.
    HRESULT hr = MFStartup(MF_VERSION);
    if (SUCCEEDED(hr))
    {
        m_hCloseEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
        if (m_hCloseEvent == NULL)
        {
            hr = HRESULT_FROM_WIN32(GetLastError());
        }
    }
    return hr;
}

//######################################
//
//######################################
CPlayer::CPlayer(HWND hVideo, HWND hEvent) :
    m_pSession(NULL),
    m_pSource(NULL),
    m_pVideoDisplay(NULL),
    m_pAudioVolume(NULL),
	m_pRateControl(NULL),
	//m_pRateSupport(NULL),
	m_pVideoProcessor(NULL),

//	m_pClock(NULL),
	m_pPresentationClock(NULL),

    m_hwndVideo(hVideo),
    m_hwndEvent(hEvent),

    m_state(Closed),
    m_hCloseEvent(NULL),
    m_nRefCount(1)

//	m_bPending(FALSE)
{
	//Clear();
}

//######################################
// Clears any resources for the current topology.
//######################################
//HRESULT CPlayer::Clear()
//{
//    //m_caps = 0;
//    m_bCanScrub = FALSE;
//
//    m_hnsDuration = 0;
//    //m_fPrevRate = 1.0f;
//
//    m_bPending = FALSE;
//
////    SafeRelease(&m_pClock);
////    SafeRelease(&m_pSession);
////    SafeRelease(&m_pRate);
////    SafeRelease(&m_pRateSupport);
//
//    ZeroMemory(&m_state, sizeof(m_state));
//    m_state.command = CmdStop;
//    m_state.fRate = 1.0f;
//
//    ZeroMemory(&m_request, sizeof(m_request));
//    m_request.command = CmdNone;
//    m_request.fRate = 1.0f;
//
//    return S_OK;
//}

//######################################
//
//######################################
CPlayer::~CPlayer()
{
    assert(m_pSession == NULL);
    // If FALSE, the app did not call Shutdown().

    // When CPlayer calls IMediaEventGenerator::BeginGetEvent on the
    // media session, it causes the media session to hold a reference
    // count on the CPlayer.

    // This creates a circular reference count between CPlayer and the
    // media session. Calling Shutdown breaks the circular reference
    // count.

    // If CreateInstance fails, the application will not call
    // Shutdown. To handle that case, call Shutdown in the destructor.

    Shutdown();
}

// IUnknown methods

HRESULT CPlayer::QueryInterface(REFIID riid, void** ppv)
{
    static const QITAB qit[] =
    {
        QITABENT(CPlayer, IMFAsyncCallback),
        { 0 }
    };
    return QISearch(this, qit, riid, ppv);
}

ULONG CPlayer::AddRef()
{
    return InterlockedIncrement(&m_nRefCount);
}

ULONG CPlayer::Release()
{
    ULONG uCount = InterlockedDecrement(&m_nRefCount);
    if (uCount == 0)
    {
        delete this;
    }
    return uCount;
}

//######################################
//  Callback for the asynchronous BeginGetEvent method.
//######################################
HRESULT CPlayer::Invoke(IMFAsyncResult *pResult)
{
    MediaEventType meType = MEUnknown;  // Event type

    IMFMediaEvent *pEvent = NULL;

    // Get the event from the event queue.
    HRESULT hr = m_pSession->EndGetEvent(pResult, &pEvent);
    if (FAILED(hr))
    {
        goto done;
    }

    // Get the event type.
    hr = pEvent->GetType(&meType);
    if (FAILED(hr))
    {
        goto done;
    }

    if (meType == MESessionClosed)
    {
        // The session was closed.
        // The application is waiting on the m_hCloseEvent event handle.
        SetEvent(m_hCloseEvent);
    }
    else
    {
        // For all other events, get the next event in the queue.
        hr = m_pSession->BeginGetEvent(this, NULL);
        if (FAILED(hr))
        {
            goto done;
        }
    }

    // Check the application state.

    // If a call to IMFMediaSession::Close is pending, it means the
    // application is waiting on the m_hCloseEvent event and
    // the application's message loop is blocked.

    // Otherwise, post a private window message to the application.

    if (m_state != Closing)
    {
        // Leave a reference count on the event.
        pEvent->AddRef();

		HandleEvent((WPARAM)pEvent);

//        PostMessage(m_hwndEvent, WM_APP_PLAYER_EVENT, (WPARAM)pEvent, (LPARAM)meType);
    }

done:
    SafeRelease(&pEvent);
    return S_OK;
}

//######################################
// Protected methods
//######################################

//######################################
//  Create a new instance of the media session.
//######################################
HRESULT CPlayer::CreateSession()
{
    // Close the old session, if any.
    HRESULT hr = CloseFile();
    if (FAILED(hr))
    {
        goto done;
    }

    assert(m_state == Closed);

    // Create the media session.
    hr = MFCreateMediaSession(NULL, &m_pSession);
    if (FAILED(hr))
    {
        goto done;
    }

    // Start pulling events from the media session
    hr = m_pSession->BeginGetEvent((IMFAsyncCallback*)this, NULL);
    if (FAILED(hr))
    {
        goto done;
    }

	m_state = Ready;

done:
    return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::HandleEvent(UINT_PTR pEventPtr)
{
    HRESULT hrStatus = S_OK;
    MediaEventType meType = MEUnknown;

    IMFMediaEvent *pEvent = (IMFMediaEvent*)pEventPtr;

    if (pEvent == NULL)
        return E_POINTER;

    // Get the event type.
    HRESULT hr = pEvent->GetType(&meType);
    if (FAILED(hr))
        goto done;

    // Get the event status. If the operation that triggered the event
    // did not succeed, the status is a failure code.
    hr = pEvent->GetStatus(&hrStatus);

    // Check if the async operation succeeded.
    if (SUCCEEDED(hr) && FAILED(hrStatus))
        hr = hrStatus;

//    if (FAILED(hr))
//        goto done;

    switch(meType)
    {
    case MESessionTopologyStatus:
        hr = OnTopologyStatus(pEvent);
        goto done;
        break;

    case MEEndOfPresentation:
        hr = OnPresentationEnded(pEvent);
        break;

    case MENewPresentation:
        hr = OnNewPresentation(pEvent);
        break;

//    case MESessionStarted:
//        OnSessionStart(hrStatus);
//        break;
//
//    case MESessionStopped:
//        OnSessionStop(hrStatus);
//        break;
//
//    case MESessionPaused:
//        OnSessionPause(hrStatus);
//        break;



//    case MESessionRateChanged:
//        // If the rate change succeeded, we've already got the rate
//        // cached. If it failed, try to get the actual rate.
//        if (FAILED(hrStatus))
//        {
//        	PROPVARIANT var;
//            PropVariantInit(&var);
//            hr = pEvent->GetValue(&var);
//            if (SUCCEEDED(hr) && (var.vt == VT_R4))
//            {
//               m_state.fRate = var.fltVal;
//            }
//
//        }
//        break;

//    case MESessionEnded:
//        OnSessionEnded(hrStatus);
//        break;
//
//    case MESessionCapabilitiesChanged:
//        // The session capabilities changed. Get the updated capabilities.
//        m_caps = MFGetAttributeUINT32(pEvent, MF_EVENT_SESSIONCAPS, m_caps);
//        break;

    }

	PostMessage(m_hwndEvent, WM_APP_PLAYER_EVENT, (WPARAM)meType, (LPARAM)hrStatus);

done:
    SafeRelease(&pEvent);
    return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::OnTopologyStatus(IMFMediaEvent *pEvent)
{
    UINT32 status;

    HRESULT hr = pEvent->GetUINT32(MF_EVENT_TOPOLOGY_STATUS, &status);
    if (SUCCEEDED(hr))
    {
    	if (status == MF_TOPOSTATUS_READY)
	    {
	        SafeRelease(&m_pVideoDisplay);
	        SafeRelease(&m_pAudioVolume);
			SafeRelease(&m_pRateControl);
			SafeRelease(&m_pVideoProcessor);

	        // Get the IMFVideoDisplayControl interface from EVR. This call is
	        // expected to fail if the media file does not have a video stream.

	        (void)MFGetService(m_pSession, MR_VIDEO_RENDER_SERVICE, IID_PPV_ARGS(&m_pVideoDisplay));

			(void)MFGetService(m_pSession, MR_POLICY_VOLUME_SERVICE, IID_PPV_ARGS(&m_pAudioVolume));

			// Get the rate control service.
			(void)MFGetService(m_pSession, MF_RATE_CONTROL_SERVICE, IID_PPV_ARGS(&m_pRateControl));

			// Check if rate 0 (scrubbing) is supported.
			// TODO: use m_pRateSupport->IsRateSupported(TRUE, 0, NULL);
//			if (m_pRateControl)
//				m_bCanScrub = TRUE;

			(void)MFGetService(m_pSession, MR_VIDEO_MIXER_SERVICE, IID_PPV_ARGS(&m_pVideoProcessor));

		    // Get the presentation clock (optional)
		    IMFClock *pClock = NULL;
		    HRESULT hrTmp = m_pSession->GetClock(&pClock);
		    if (SUCCEEDED(hrTmp))
		    {
		        hr = pClock->QueryInterface(IID_PPV_ARGS(&m_pPresentationClock));
//		        if (FAILED(hr))
//		        {
//		            goto done;
//		        }
				SafeRelease(&pClock);
		    }

		    // Get the rate control interface (optional)
		    //hrTmp = MFGetService(m_pSession, MF_RATE_CONTROL_SERVICE, IID_PPV_ARGS(&m_pRateControl));

		    //// Get the rate support interface (optional)
		    //if (SUCCEEDED(hrTmp))
		    //{
		    //    hrTmp = MFGetService(m_pSession, MF_RATE_CONTROL_SERVICE, IID_PPV_ARGS(&m_pRateSupport));
		    //}
		    //if (SUCCEEDED(hrTmp))
		    //{
		    //   //  Check if rate 0 (scrubbing) is supported.
		    //    hrTmp = m_pRateSupport->IsRateSupported(TRUE, 0, NULL);
		    //}
		    //if (SUCCEEDED(hrTmp))
		    //{
		    //    m_bCanScrub = TRUE;
		    //}

		    //// if m_pRateControl is NULL, m_bCanScrub must be FALSE.
		    //assert(m_pRateControl || !m_bCanScrub);

		}

		PostMessage(m_hwndEvent, WM_APP_PLAYER_EVENT, (WPARAM)MESessionTopologyStatus, (LPARAM)status);
    }
    return hr;
}

//######################################
//  Handler for MEEndOfPresentation event.
//######################################
HRESULT CPlayer::OnPresentationEnded(IMFMediaEvent *pEvent)
{
    // The session puts itself into the stopped state automatically.
	m_state = Stopped;
    return S_OK;
}

//######################################
//  Handler for MENewPresentation event.
//
//  This event is sent if the media source has a new presentation, which
//  requires a new topology.
//######################################
HRESULT CPlayer::OnNewPresentation(IMFMediaEvent *pEvent)
{
    IMFPresentationDescriptor *pPD = NULL;
    IMFTopology *pTopology = NULL;

    // Get the presentation descriptor from the event.
    HRESULT hr = GetEventObject(pEvent, &pPD);
    if (FAILED(hr))
    {
        goto done;
    }

    // Create a partial topology.
    hr = CreatePlaybackTopology(m_pSource, pPD, m_hwndVideo, &pTopology);
    if (FAILED(hr))
    {
        goto done;
    }

    // Set the topology on the media session.
    hr = m_pSession->SetTopology(0, pTopology);
    if (FAILED(hr))
    {
        goto done;
    }

	m_state = OpenPending;

done:
    SafeRelease(&pTopology);
    SafeRelease(&pPD);
    return S_OK;
}

//######################################
//  Create a media source from a URL.
//######################################
HRESULT CreateMediaSource(PCWSTR sURL, IMFMediaSource **ppSource)
{
    MF_OBJECT_TYPE ObjectType = MF_OBJECT_INVALID;

    IMFSourceResolver* pSourceResolver = NULL;
    IUnknown* pSource = NULL;

    // Create the source resolver.
    HRESULT hr = MFCreateSourceResolver(&pSourceResolver);
    if (FAILED(hr))
    {
        goto done;
    }

    // Use the source resolver to create the media source.

    // Note: For simplicity this sample uses the synchronous method to create
    // the media source. However, creating a media source can take a noticeable
    // amount of time, especially for a network source. For a more responsive
    // UI, use the asynchronous BeginCreateObjectFromURL method.
    hr = pSourceResolver->CreateObjectFromURL(
        sURL,                       // URL of the source.
        MF_RESOLUTION_MEDIASOURCE,  // Create a source object.
        NULL,                       // Optional property store.
        &ObjectType,        // Receives the created object type.
        &pSource            // Receives a pointer to the media source.
        );
    if (FAILED(hr))
    {
        goto done;
    }

    // Get the IMFMediaSource interface from the media source.
    hr = pSource->QueryInterface(IID_PPV_ARGS(ppSource));

done:
    SafeRelease(&pSourceResolver);
    SafeRelease(&pSource);
    return hr;
}

//######################################
//  Create an activation object for a renderer, based on the stream media type.
//######################################
HRESULT CreateMediaSinkActivate(
    IMFStreamDescriptor *pSourceSD,     // Pointer to the stream descriptor.
    HWND hVideoWindow,                  // Handle to the video clipping window.
    IMFActivate **ppActivate
)
{
    IMFMediaTypeHandler *pHandler = NULL;
    IMFActivate *pActivate = NULL;

    // Get the media type handler for the stream.
    HRESULT hr = pSourceSD->GetMediaTypeHandler(&pHandler);
    if (FAILED(hr))
    {
        goto done;
    }

    // Get the major media type.
    GUID guidMajorType;
    hr = pHandler->GetMajorType(&guidMajorType);
    if (FAILED(hr))
    {
        goto done;
    }

    // Create an IMFActivate object for the renderer, based on the media type.
    if (MFMediaType_Audio == guidMajorType)
    {
        // Create the audio renderer.
        hr = MFCreateAudioRendererActivate(&pActivate);
    }
    else if (MFMediaType_Video == guidMajorType)
    {
        // Create the video renderer.
        hr = MFCreateVideoRendererActivate(hVideoWindow, &pActivate);
    }
    else
    {
        // Unknown stream type.
        hr = E_FAIL;
        // Optionally, you could deselect this stream instead of failing.
    }
    if (FAILED(hr))
    {
        goto done;
    }

    // Return IMFActivate pointer to caller.
    *ppActivate = pActivate;
    (*ppActivate)->AddRef();

done:
    SafeRelease(&pHandler);
    SafeRelease(&pActivate);
    return hr;
}

//######################################
// Add a source node to a topology.
//######################################
HRESULT AddSourceNode(
    IMFTopology *pTopology,           // Topology.
    IMFMediaSource *pSource,          // Media source.
    IMFPresentationDescriptor *pPD,   // Presentation descriptor.
    IMFStreamDescriptor *pSD,         // Stream descriptor.
    IMFTopologyNode **ppNode)         // Receives the node pointer.
{
    IMFTopologyNode *pNode = NULL;

    // Create the node.
    HRESULT hr = MFCreateTopologyNode(MF_TOPOLOGY_SOURCESTREAM_NODE, &pNode);
    if (FAILED(hr))
    {
        goto done;
    }

    // Set the attributes.
    hr = pNode->SetUnknown(MF_TOPONODE_SOURCE, pSource);
    if (FAILED(hr))
    {
        goto done;
    }

    hr = pNode->SetUnknown(MF_TOPONODE_PRESENTATION_DESCRIPTOR, pPD);
    if (FAILED(hr))
    {
        goto done;
    }

    hr = pNode->SetUnknown(MF_TOPONODE_STREAM_DESCRIPTOR, pSD);
    if (FAILED(hr))
    {
        goto done;
    }

    // Add the node to the topology.
    hr = pTopology->AddNode(pNode);
    if (FAILED(hr))
    {
        goto done;
    }

    // Return the pointer to the caller.
    *ppNode = pNode;
    (*ppNode)->AddRef();

done:
    SafeRelease(&pNode);
    return hr;
}

//######################################
// Add an output node to a topology.
//######################################
HRESULT AddOutputNode(
    IMFTopology *pTopology,     // Topology.
    IMFActivate *pActivate,     // Media sink activation object.
    DWORD dwId,                 // Identifier of the stream sink.
    IMFTopologyNode **ppNode)   // Receives the node pointer.
{
    IMFTopologyNode *pNode = NULL;

    // Create the node.
    HRESULT hr = MFCreateTopologyNode(MF_TOPOLOGY_OUTPUT_NODE, &pNode);
    if (FAILED(hr))
    {
        goto done;
    }

    // Set the object pointer.
    hr = pNode->SetObject(pActivate);
    if (FAILED(hr))
    {
        goto done;
    }

    // Set the stream sink ID attribute.
    hr = pNode->SetUINT32(MF_TOPONODE_STREAMID, dwId);
    if (FAILED(hr))
    {
        goto done;
    }

    hr = pNode->SetUINT32(MF_TOPONODE_NOSHUTDOWN_ON_REMOVE, FALSE);
    if (FAILED(hr))
    {
        goto done;
    }

    // Add the node to the topology.
    hr = pTopology->AddNode(pNode);
    if (FAILED(hr))
    {
        goto done;
    }

    // Return the pointer to the caller.
    *ppNode = pNode;
    (*ppNode)->AddRef();

done:
    SafeRelease(&pNode);
    return hr;
}

//######################################
//  Add a topology branch for one stream.
//
//  For each stream, this function does the following:
//
//    1. Creates a source node associated with the stream.
//    2. Creates an output node for the renderer.
//    3. Connects the two nodes.
//
//  The media session will add any decoders that are needed.
//######################################
HRESULT AddBranchToPartialTopology(
    IMFTopology *pTopology,         // Topology.
    IMFMediaSource *pSource,        // Media source.
    IMFPresentationDescriptor *pPD, // Presentation descriptor.
    DWORD iStream,                  // Stream index.
    HWND hVideoWnd)                 // Window for video playback.
{
    IMFStreamDescriptor *pSD = NULL;
    IMFActivate         *pSinkActivate = NULL;
    IMFTopologyNode     *pSourceNode = NULL;
    IMFTopologyNode     *pOutputNode = NULL;

    BOOL fSelected = FALSE;

    HRESULT hr = pPD->GetStreamDescriptorByIndex(iStream, &fSelected, &pSD);
    if (FAILED(hr))
        goto done;

    if (fSelected)
    {
        // Create the media sink activation object.
        hr = CreateMediaSinkActivate(pSD, hVideoWnd, &pSinkActivate);
        if (FAILED(hr))
            goto done;

        // Add a source node for this stream.
        hr = AddSourceNode(pTopology, pSource, pPD, pSD, &pSourceNode);
        if (FAILED(hr))
            goto done;

        // Create the output node for the renderer.
        hr = AddOutputNode(pTopology, pSinkActivate, 0, &pOutputNode);
        if (FAILED(hr))
            goto done;


        // Connect the source node to the output node.
        hr = pSourceNode->ConnectOutput(0, pOutputNode, 0);
    }
    // else: If not selected, don't add the branch.

done:
    SafeRelease(&pSD);
    SafeRelease(&pSinkActivate);
    SafeRelease(&pSourceNode);
    SafeRelease(&pOutputNode);
    return hr;
}

//######################################
//
//######################################
HRESULT SetPlaybackOptimizations(IMFTopology *pTopology, HWND hwnd)
{
    HRESULT hr = pTopology->SetUINT32(
        MF_TOPOLOGY_STATIC_PLAYBACK_OPTIMIZATIONS, TRUE);

    if (FAILED(hr))
    {
        return hr;
    }

    HMONITOR hCurrentMon = MonitorFromWindow(hwnd, MONITOR_DEFAULTTOPRIMARY);

    if (hCurrentMon)
    {
        MONITORINFO MonitorInfo = {0};
        MonitorInfo.cbSize = sizeof(MONITORINFO);

        BOOL fSucceeded = GetMonitorInfo(hCurrentMon, &MonitorInfo);

        if (fSucceeded )
        {
            const RECT& rcMonitor = MonitorInfo.rcMonitor;

            LONG width = rcMonitor.right - rcMonitor.left;
            LONG height = rcMonitor.bottom - rcMonitor.top;

            hr = MFSetAttributeSize(
                pTopology,
                MF_TOPOLOGY_PLAYBACK_MAX_DIMS,
                (UINT32)width, (UINT32)height
                );

            if (FAILED(hr))
            {
                goto done;
            }

            HDC hdc = GetDC(hwnd);

            hr = MFSetAttributeRatio(
                pTopology,
                MF_TOPOLOGY_PLAYBACK_FRAMERATE,
                GetDeviceCaps(hdc, VREFRESH), 1
                );

            ReleaseDC(hwnd, hdc);
        }
    }
done:
    return hr;
}

//######################################
//  Create a playback topology from a media source.
//######################################
HRESULT CreatePlaybackTopology(
    IMFMediaSource *pSource,          // Media source.
    IMFPresentationDescriptor *pPD,   // Presentation descriptor.
    HWND hVideoWnd,                   // Video window.
    IMFTopology **ppTopology)         // Receives a pointer to the topology.
{
    IMFTopology *pTopology = NULL;
    DWORD cSourceStreams = 0;

    // Create a new topology.
    HRESULT hr = MFCreateTopology(&pTopology);
    if (FAILED(hr))
    {
        goto done;
    }

    // Get the number of streams in the media source.
    hr = pPD->GetStreamDescriptorCount(&cSourceStreams);
    if (FAILED(hr))
    {
        goto done;
    }

    // For each stream, create the topology nodes and add them to the topology.
    for (DWORD i = 0; i < cSourceStreams; i++)
    {
        hr = AddBranchToPartialTopology(pTopology, pSource, pPD, i, hVideoWnd);
        if (FAILED(hr))
        {
            goto done;
        }
    }

//	hr = pTopology->SetUINT32(MF_TOPOLOGY_STATIC_PLAYBACK_OPTIMIZATIONS, TRUE);

	SetPlaybackOptimizations(pTopology, hVideoWnd);

    // Return the IMFTopology pointer to the caller.
    *ppTopology = pTopology;
    (*ppTopology)->AddRef();

done:
    SafeRelease(&pTopology);
    return hr;
}
