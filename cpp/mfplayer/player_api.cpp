#include "player.h"

#include <stdio.h>

//######################################
//
//######################################
HRESULT CPlayer::CloseFile()
{
    //  The IMFMediaSession::Close method is asynchronous, but the
    //  CPlayer::CloseSession method waits on the MESessionClosed event.
    //
    //  MESessionClosed is guaranteed to be the last event that the
    //  media session fires.

    HRESULT hr = S_OK;

    SafeRelease(&m_pVideoDisplay);
    SafeRelease(&m_pAudioVolume);
	SafeRelease(&m_pRateControl);
	SafeRelease(&m_pVideoProcessor);
	SafeRelease(&m_pPresentationClock);

    // First close the media session.
    if (m_pSession)
    {
        DWORD dwWaitResult = 0;

        m_state = Closing;

        hr = m_pSession->Close();
        // Wait for the close operation to complete
        if (SUCCEEDED(hr))
        {
            dwWaitResult = WaitForSingleObject(m_hCloseEvent, 5000);
            if (dwWaitResult == WAIT_TIMEOUT)
            {
                assert(FALSE);
            }
            // Now there will be no more events from this session.
        }
    }

    // Complete shutdown operations.
    if (SUCCEEDED(hr))
    {
        // Shut down the media source. (Synchronous operation, no events.)
        if (m_pSource)
        {
            (void)m_pSource->Shutdown();
        }
        // Shut down the media session. (Synchronous operation, no events.)
        if (m_pSession)
        {
            (void)m_pSession->Shutdown();
        }
    }

    SafeRelease(&m_pSource);
    SafeRelease(&m_pSession);
    m_state = Closed;

    return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::GetAspectRatio(LPDWORD pRatio)
{
	if (pRatio == NULL)
		return E_POINTER;
	if (m_pVideoDisplay == NULL)
		return E_UNEXPECTED;
	SIZE ratio = {};
	//HRESULT hr = m_pPlayer->GetNativeVideoSize(NULL, &ratio);
	HRESULT hr = m_pVideoDisplay->GetNativeVideoSize(NULL, &ratio);
	if (SUCCEEDED(hr))
		*pRatio = MAKELONG(ratio.cx, ratio.cy);
	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::GetCapabilities(LPDWORD pdwCaps)
{
    if (pdwCaps == NULL)
        return E_POINTER;

	if (m_pSession == NULL)
		return E_UNEXPECTED;
	return m_pSession->GetSessionCapabilities(pdwCaps);
}

//######################################
//
//######################################
HRESULT CPlayer::GetCharacteristics(LPDWORD pdwChars)
{
    if (pdwChars == NULL)
        return E_POINTER;

	if (m_pSource == NULL)
		return E_UNEXPECTED;

	return m_pSource->GetCharacteristics(pdwChars);
}

//######################################
//
//######################################
HRESULT CPlayer::GetCurrentImage(BITMAPINFOHEADER *pBih, BYTE **pDib, DWORD *pcbDib, LONGLONG *pTimeStamp)
{
//	if (pSize == NULL)
//		return E_POINTER;

	if (m_pVideoDisplay == NULL)
		return E_UNEXPECTED;

	return m_pVideoDisplay->GetCurrentImage(pBih, pDib, pcbDib, pTimeStamp);
}

//######################################
//
//######################################
HRESULT CPlayer::GetDuration(MFTIME *pDuration)
{
    if (pDuration == NULL)
        return E_POINTER;

	if (m_pSource == NULL)
		return E_UNEXPECTED;

	IMFPresentationDescriptor *pPD = NULL;
	HRESULT hr = m_pSource->CreatePresentationDescriptor(&pPD);
	if (SUCCEEDED(hr))
	{
		hr = pPD->GetUINT64(MF_PD_DURATION, (UINT64*)pDuration);
		pPD->Release();
	}
	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::GetFrameRate(float *pfRate)
{
//    if (pfRate == NULL)
//        return E_POINTER;

	if (m_pSource == NULL)
		return E_UNEXPECTED;

	UINT32 num = 0;
	UINT32 denom = 0;

	IMFPresentationDescriptor *pPD = NULL;
	HRESULT hr = m_pSource->CreatePresentationDescriptor(&pPD);
	if (SUCCEEDED(hr))
	{
		DWORD cnt;
		hr = pPD->GetStreamDescriptorCount(&cnt);

		BOOL selected;
		for (DWORD idx = 0; idx < cnt; idx++)
		{
			IMFStreamDescriptor *pDescriptor;
			hr = pPD->GetStreamDescriptorByIndex(idx, &selected, &pDescriptor);
			if (SUCCEEDED(hr) && selected)
			{
				IMFMediaTypeHandler *pMediaTypeHandler;
				hr = pDescriptor->GetMediaTypeHandler(&pMediaTypeHandler);
				if (SUCCEEDED(hr))
				{
					IMFMediaType *pType;
					pMediaTypeHandler->GetCurrentMediaType(&pType);

					GUID guidMajorType;
					hr = pType->GetGUID(MF_MT_MAJOR_TYPE, &guidMajorType);
					if (guidMajorType == MFMediaType_Video)
					{
						hr = MFGetAttributeRatio(pType, MF_MT_FRAME_RATE, &num, &denom);

//						#define DBGI(x) {char dbg[32];sprintf(dbg,"%ld",x);OutputDebugStringA(dbg);}
//						DBGI(num)
//						DBGI(denom)

						pMediaTypeHandler->Release();
						pMediaTypeHandler->Release();
						break;
					}

					pMediaTypeHandler->Release();
				}
				pDescriptor->Release();
			}
		}

		pPD->Release();
	}
	//MAKELONG((WORD)num, (WORD)denom)

	//#define DBGI(x) {char dbg[32];sprintf(dbg,"%ld",x);OutputDebugStringA(dbg);}
	//DBGI(num)
	//DBGI(denom)

	if (SUCCEEDED(hr))
		*pfRate = (float)num / (float)denom;

	return hr;
}

#define KnownKey(a, b, c) if (key == a) { wcscpy_s(key_name, 40, b); return c; };

VARENUM handle_key(PROPERTYKEY key, wchar_t *key_name)
{
	KnownKey(MFPKEY_Content_DLNA_Profile_ID, L"Content_DLNA_Profile_ID", VT_LPWSTR)
		KnownKey(PKEY_Audio_ChannelCount, L"Audio_ChannelCount", VT_UI4)
		KnownKey(PKEY_Audio_EncodingBitrate, L"Audio_EncodingBitrate", VT_UI4)
		KnownKey(PKEY_Audio_Format, L"Audio_Format", VT_LPWSTR)
		KnownKey(PKEY_Audio_IsVariableBitRate, L"Audio_IsVariableBitRate", VT_BOOL)
		KnownKey(PKEY_Audio_PeakValue, L"Audio_PeakValue", VT_UI4)
		KnownKey(PKEY_Audio_SampleRate, L"Audio_SampleRate", VT_UI4)
		KnownKey(PKEY_Audio_SampleSize, L"Audio_SampleSize", VT_UI4)
		KnownKey(PKEY_Audio_StreamNumber, L"Audio_StreamNumber", VT_UI4)
		KnownKey(PKEY_Author, L"Author", VT_LPWSTR)
		KnownKey(PKEY_Comment, L"Comment", VT_LPWSTR)
		KnownKey(PKEY_Copyright, L"Copyright", VT_LPWSTR)
		KnownKey(PKEY_DRM_IsProtected, L"DRM_IsProtected", VT_BOOL)
		KnownKey(PKEY_Keywords, L"Keywords", VT_LPWSTR)
		KnownKey(PKEY_Language, L"Language", VT_LPWSTR)
		KnownKey(PKEY_Media_AuthorUrl, L"Media_AuthorUrl", VT_LPWSTR)
		KnownKey(PKEY_Media_AverageLevel, L"Media_AverageLevel", VT_UI4)
		KnownKey(PKEY_Media_ClassPrimaryID, L"Media_ClassPrimaryID", VT_LPWSTR)
		KnownKey(PKEY_Media_ClassSecondaryID, L"Media_ClassSecondaryID", VT_LPWSTR)
		KnownKey(PKEY_Media_CollectionGroupID, L"Media_CollectionGroupID", VT_LPWSTR)
		KnownKey(PKEY_Media_CollectionID, L"Media_CollectionID", VT_LPWSTR)
		KnownKey(PKEY_Media_ContentDistributor, L"Media_ContentDistributor", VT_LPWSTR)
		KnownKey(PKEY_Media_ContentID, L"Media_ContentID", VT_LPWSTR)
		KnownKey(PKEY_Media_DateEncoded, L"Media_DateEncoded", VT_FILETIME)
		KnownKey(PKEY_Media_DateReleased, L"Media_DateReleased", VT_LPWSTR)
		KnownKey(PKEY_Media_Duration, L"Media_Duration", VT_UI8)
		KnownKey(PKEY_Media_DVDID, L"Media_DVDID", VT_LPWSTR)
		KnownKey(PKEY_Media_EncodedBy, L"Media_EncodedBy", VT_LPWSTR)
		KnownKey(PKEY_Media_EncodingSettings, L"Media_EncodingSettings", VT_LPWSTR)
		KnownKey(PKEY_Media_MCDI, L"Media_MCDI", VT_LPWSTR)
		KnownKey(PKEY_Media_MetadataContentProvider, L"Media_MetadataContentProvider", VT_LPWSTR)
		KnownKey(PKEY_Media_Producer, L"Media_Producer", VT_LPWSTR)
		KnownKey(PKEY_Media_PromotionUrl, L"Media_PromotionUrl", VT_LPWSTR)
		KnownKey(PKEY_Media_ProviderRating, L"Media_ProviderRating", VT_LPWSTR)
		KnownKey(PKEY_Media_ProviderStyle, L"Media_ProviderStyle", VT_LPWSTR)
		KnownKey(PKEY_Media_Publisher, L"Media_Publisher", VT_LPWSTR)
		KnownKey(PKEY_Media_SubTitle, L"Media_SubTitle", VT_LPWSTR)
		KnownKey(PKEY_Media_UniqueFileIdentifier, L"Media_UniqueFileIdentifier", VT_LPWSTR)
		KnownKey(PKEY_Media_Writer, L"Media_Writer", VT_LPWSTR)
		KnownKey(PKEY_Media_Year, L"Media_Year", VT_UI4)
		KnownKey(PKEY_Music_AlbumArtist, L"Music_AlbumArtist", VT_LPWSTR)
		KnownKey(PKEY_Music_AlbumTitle, L"Music_AlbumTitle", VT_LPWSTR)
		KnownKey(PKEY_Music_Artist, L"Music_Artist", VT_LPWSTR)
		KnownKey(PKEY_Music_BeatsPerMinute, L"Music_BeatsPerMinute", VT_LPWSTR)
		KnownKey(PKEY_Music_Composer, L"Music_Composer", VT_LPWSTR)
		KnownKey(PKEY_Music_Conductor, L"Music_Conductor", VT_LPWSTR)
		KnownKey(PKEY_Music_ContentGroupDescription, L"Music_ContentGroupDescription", VT_LPWSTR)
		KnownKey(PKEY_Music_Genre, L"Music_Genre", VT_LPWSTR)
		KnownKey(PKEY_Music_InitialKey, L"Music_InitialKey", VT_LPWSTR)
		KnownKey(PKEY_Music_IsCompilation, L"Music_IsCompilation", VT_BOOL)
		KnownKey(PKEY_Music_Lyrics, L"Music_Lyrics", VT_LPWSTR)
		KnownKey(PKEY_Music_Mood, L"Music_Mood", VT_LPWSTR)
		KnownKey(PKEY_Music_PartOfSet, L"Music_PartOfSet", VT_LPWSTR)
		KnownKey(PKEY_Music_Period, L"Music_Period", VT_LPWSTR)
		KnownKey(PKEY_Music_TrackNumber, L"Music_TrackNumber", VT_UI4)
		KnownKey(PKEY_ParentalRating, L"ParentalRating", VT_LPWSTR)
		KnownKey(PKEY_ParentalRatingReason, L"ParentalRatingReason", VT_LPWSTR)
		KnownKey(PKEY_Rating, L"Rating", VT_UI4)
		KnownKey(PKEY_Title, L"Title", VT_LPWSTR)
		KnownKey(PKEY_Video_Compression, L"Video_Compression", VT_LPWSTR)
		KnownKey(PKEY_Video_Director, L"Video_Director", VT_LPWSTR)
		KnownKey(PKEY_Video_EncodingBitrate, L"Video_EncodingBitrate", VT_UI4)
		KnownKey(PKEY_Video_FourCC, L"Video_FourCC", VT_UI4)
		KnownKey(PKEY_Video_FrameHeight, L"Video_FrameHeight", VT_UI4)
		KnownKey(PKEY_Video_FrameRate, L"Video_FrameRate", VT_UI4)
		KnownKey(PKEY_Video_FrameWidth, L"Video_FrameWidth", VT_UI4)
		KnownKey(PKEY_Video_HorizontalAspectRatio, L"Video_HorizontalAspectRatio", VT_UI4)
		KnownKey(PKEY_Video_IsStereo, L"Video_IsStereo", VT_BOOL)
		KnownKey(PKEY_Video_StreamNumber, L"Video_StreamNumber", VT_UI4)
		KnownKey(PKEY_Video_TotalBitrate, L"Video_TotalBitrate", VT_UI4)
		KnownKey(PKEY_Video_VerticalAspectRatio, L"Video_VerticalAspectRatio", VT_UI4)
		return VT_EMPTY;
}

#define ENSURE_SIZE(a) if (pos + 2 * (wcslen(a) + 1) > buf_size) {\
	buf_size += 1024;\
	LPWSTR buf_new = (LPWSTR)CoTaskMemRealloc((LPVOID)buf, buf_size);\
	if (buf_new) buf = buf_new;\
	else {CoTaskMemFree(buf); hr = E_OUTOFMEMORY; goto done;}\
}

//######################################
//
//######################################
HRESULT CPlayer::GetMetadata(BYTE **pData, DWORD *pDataSize)
{
	if (m_pSource == NULL)
		return E_UNEXPECTED;

	HRESULT hr = S_OK;

	IPropertyStore *pProp;
	hr = MFGetService(m_pSource, MF_PROPERTY_HANDLER_SERVICE, IID_PPV_ARGS(&pProp));

	if (FAILED(hr))
		return hr;

	DWORD buf_size = 2048;  // 2 KB
	LPWSTR buf = (LPWSTR)CoTaskMemAlloc(10240);

	LPWSTR buf_new = (LPWSTR)CoTaskMemRealloc((LPVOID)buf, buf_size);
	if (buf_new)
		buf = buf_new;

	if (buf == NULL)
	{
		hr = E_OUTOFMEMORY;
		goto done;
	}

	buf[0] = L'\0';

	DWORD cnt;
	hr = pProp->GetCount(&cnt);
	if (FAILED(hr))
		return hr;

	PROPERTYKEY key;
	PROPVARIANT val;

	size_t pos = 0;
	wchar_t key_name[40];
	wchar_t num[40];

	VARENUM data_type;

	for (DWORD i = 0; i < cnt; i++)
	{
		pProp->GetAt(i, &key);
		pProp->GetValue(key, &val);

		data_type = handle_key(key, key_name);
		if (data_type == VT_EMPTY)
			continue;

		ENSURE_SIZE(key_name)
		wcscat_s(buf, buf_size, key_name);
		wcscat_s(buf, buf_size, L"\t");
		pos += 2 * (wcslen(key_name) + 1);

		if (val.vt == VT_LPWSTR)
		{
			ENSURE_SIZE(val.pwszVal)
			wcscat_s(buf, buf_size, val.pwszVal);
			wcscat_s(buf, buf_size, L"\n");
			pos += 2 * (wcslen(val.pwszVal) + 1);
		}
		else if (val.vt == VT_UI4)
		{
			wsprintf(num, L"%lu", val.uintVal);

			ENSURE_SIZE(num)
			wcscat_s(buf, buf_size, num);
			wcscat_s(buf, buf_size, L"\n");
			pos += 2 * (wcslen(num) + 1);
		}
		else if (val.vt == VT_UI8)
		{
			wsprintf(num, L"%lu", val.ulVal);

			ENSURE_SIZE(num)
			wcscat_s(buf, buf_size, num);
			wcscat_s(buf, buf_size, L"\n");
			pos += 2 * (wcslen(num) + 1);
		}
		else if (val.vt == VT_FILETIME)
		{
			DWORD flags = FDTF_DEFAULT;
			SHFormatDateTimeW(&val.filetime, &flags, num, 40);

			ENSURE_SIZE(num)
			wcscat_s(buf, buf_size, num);
			wcscat_s(buf, buf_size, L"\n");
			pos += 2 * (wcslen(num) + 1);
		}
		else if (val.vt == VT_BOOL)
		{
			wsprintf(num, L"%ld", val.boolVal);

			ENSURE_SIZE(num)
			wcscat_s(buf, buf_size, num);
			wcscat_s(buf, buf_size, L"\n");
			pos += 2 * (wcslen(num) + 1);
		}
	}

	buf = (LPWSTR)CoTaskMemRealloc((LPVOID)buf, pos + 2);

	*pData = (BYTE *)buf;
	*pDataSize = pos + 2;

done:
	pProp->Release();

	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::GetMute(LPBOOL pbMute)
{
    if (pbMute == NULL)
        return E_POINTER;

    if (m_pAudioVolume == NULL)
        return E_UNEXPECTED;

	return m_pAudioVolume->GetMute(pbMute);
}

//######################################
//
//######################################
HRESULT CPlayer::GetRate(float *pfRate)
{
    if (pfRate == NULL)
        return E_POINTER;

	if (m_pRateControl == NULL)
		return E_UNEXPECTED;

	return m_pRateControl->GetRate(FALSE, pfRate);
}

//######################################
//
//######################################
HRESULT CPlayer::GetSize(LPDWORD pSize)
{
    if (pSize == NULL)
        return E_POINTER;

    if (m_pVideoDisplay == NULL)
        return E_UNEXPECTED;

	SIZE size;
	HRESULT hr = m_pVideoDisplay->GetNativeVideoSize(&size, NULL);
	if (SUCCEEDED(hr))
		*pSize = MAKELONG(size.cx, size.cy);
	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::GetState(PlayerState *pState)
{
    if (pState == NULL)
        return E_POINTER;

    *pState = m_state;
    return S_OK;
}

//######################################
//
//######################################
HRESULT CPlayer::GetStream(DWORD idx, LPDWORD pType, LPDWORD pFourCC, LPBOOL pSelected, LPWSTR lang, size_t lang_buf_size)
{
	if (pType == NULL || pFourCC == NULL || pSelected == NULL)
		return E_POINTER;

	if (m_pSource == NULL)
		return E_UNEXPECTED;

	IMFPresentationDescriptor *pPD = NULL;
	HRESULT hr = m_pSource->CreatePresentationDescriptor(&pPD);
	if (SUCCEEDED(hr))
	{
		IMFStreamDescriptor *pDescriptor;
		hr = pPD->GetStreamDescriptorByIndex(idx, pSelected, &pDescriptor);
		if (SUCCEEDED(hr))
		{
			IMFMediaTypeHandler *pMediaTypeHandler;
			hr = pDescriptor->GetMediaTypeHandler(&pMediaTypeHandler);
			if (SUCCEEDED(hr))
			{
				GUID guidMajorType;
				pMediaTypeHandler->GetMajorType(&guidMajorType);
				if (guidMajorType == MFMediaType_Video)
					*pType = 0;
				else if (guidMajorType == MFMediaType_Audio)
					*pType = 1;
				else
					*pType = 2;

				IMFMediaType *pMediaType;
				DWORD cnt;
				if (SUCCEEDED(pMediaTypeHandler->GetMediaTypeCount(&cnt)) && cnt);
				{
					if (SUCCEEDED(pMediaTypeHandler->GetMediaTypeByIndex(0, &pMediaType)))
					{
						GUID guid;
						if (SUCCEEDED(pMediaType->GetGUID(MF_MT_SUBTYPE, &guid)))
							*pFourCC = guid.Data1;
					}
				}

				pMediaTypeHandler->Release();
			}

			if (lang && lang_buf_size)
				pDescriptor->GetString(MF_SD_LANGUAGE, lang, lang_buf_size, NULL);

			pDescriptor->Release();
		}
		pPD->Release();
	}
	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::GetStreamCount(LPDWORD pCount)
{
    if (pCount == NULL)
        return E_POINTER;

	if (m_pSource == NULL)
		return E_UNEXPECTED;

	IMFPresentationDescriptor *pPD = NULL;
	HRESULT hr = m_pSource->CreatePresentationDescriptor(&pPD);
	if (SUCCEEDED(hr))
	{
		hr = pPD->GetStreamDescriptorCount(pCount);
		pPD->Release();
	}
	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::GetTime(MFTIME *phnsTime)
{
	if (phnsTime == NULL)
		return E_POINTER;

	if (m_pPresentationClock == NULL)
		return E_UNEXPECTED;
	return m_pPresentationClock->GetTime(phnsTime);
}

//######################################
//
//######################################
HRESULT CPlayer::GetVolume(float *pfLevel)
{
    if (pfLevel == NULL)
        return E_POINTER;

    if (m_pAudioVolume == NULL)
        return E_UNEXPECTED;

	return m_pAudioVolume->GetMasterVolume(pfLevel);
}

//######################################
//
//######################################
HRESULT CPlayer::HasAudio(LPBOOL pHasAudio)
{
	*pHasAudio = m_pAudioVolume != NULL;
	return S_OK;
}

//######################################
//
//######################################
HRESULT CPlayer::HasVideo(LPBOOL pHasVideo)
{
	*pHasVideo = m_pVideoDisplay != NULL;
	return S_OK;
}

//######################################
//  Open a URL for playback.
//######################################
HRESULT CPlayer::LoadFile(const WCHAR *sURL)
{
    // 1. Create a new media session.
    // 2. Create the media source.
    // 3. Create the topology.
    // 4. Queue the topology [asynchronous]
    // 5. Start playback [asynchronous - does not happen in this method.]

    IMFTopology *pTopology = NULL;
    IMFPresentationDescriptor* pSourcePD = NULL;

    // Create the media session.
    HRESULT hr = CreateSession();
    if (FAILED(hr))
    {
        goto done;
    }

    // Create the media source.
    hr = CreateMediaSource(sURL, &m_pSource);
    if (FAILED(hr))
    {
        goto done;
    }

    // Create the presentation descriptor for the media source.
    hr = m_pSource->CreatePresentationDescriptor(&pSourcePD);
    if (FAILED(hr))
    {
        goto done;
    }

    // Create a partial topology.
    hr = CreatePlaybackTopology(m_pSource, pSourcePD, m_hwndVideo, &pTopology);
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

    // If SetTopology succeeds, the media session will queue an
    // MESessionTopologySet event.

done:
    if (FAILED(hr))
    {
        m_state = Closed;
    }

    SafeRelease(&pSourcePD);
    SafeRelease(&pTopology);
    return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::Pause()
{
    if (m_pSession == NULL)
        return E_UNEXPECTED;

//    if (m_state != Playing)
//        return MF_E_INVALIDREQUEST;

    HRESULT hr = m_pSession->Pause();
    if (SUCCEEDED(hr))
        m_state = Paused;

    return hr;
}

//######################################
//  Start playback from paused or stopped.
//######################################
HRESULT CPlayer::Play()
{
    if (m_pSession == NULL)
        return E_UNEXPECTED;

	//if (m_state != Paused && m_state != Stopped)
	//    return MF_E_INVALIDREQUEST;

	PROPVARIANT var;
	PropVariantInit(&var);
	HRESULT hr = m_pSession->Start(NULL, &var);
	if (SUCCEEDED(hr))
		m_state = Playing;
	PropVariantClear(&var);

	return hr;
}

//######################################
//  Repaint the video window. Call this method on WM_PAINT.
//######################################
HRESULT CPlayer::Repaint()
{
    if (m_pVideoDisplay)
        return m_pVideoDisplay->RepaintVideo();

    return S_OK;
}

//######################################
//  Resize the video rectangle.
//  Call this method if the size of the video window changes.
//######################################
HRESULT CPlayer::ResizeVideo(WORD width, WORD height)
{
    if (m_pVideoDisplay)
    {
        // Set the destination rectangle.
        // Leave the default source rectangle (0,0,1,1).
        RECT rcDest = { 0, 0, width, height };
        return m_pVideoDisplay->SetVideoPosition(NULL, &rcDest);
    }
    return S_OK;
}

//######################################
//
//######################################
HRESULT CPlayer::SelectAudioStream(DWORD idx)
{
	if (m_pSource == NULL)
		return E_UNEXPECTED;

	HRESULT hr = S_OK;

	IMFTopology *pTopology = NULL;
	IMFPresentationDescriptor *pPD = NULL;

	MFTIME time;
	GetTime(&time);

//	SetTime(0);

	// Do not modify the presentation descriptor unless the source is stopped
	if (m_state == Playing || m_state == Paused)
		m_pSession->Stop();

	hr = m_pSource->CreatePresentationDescriptor(&pPD);
	if (SUCCEEDED(hr))
	{
		DWORD cnt;
		BOOL selected;

		hr = pPD->GetStreamDescriptorCount(&cnt);
		if (FAILED(hr))
			goto done;

		for (DWORD i = 0; i < cnt; i++)
		{
			IMFStreamDescriptor *pDescriptor;
			hr = pPD->GetStreamDescriptorByIndex(i, &selected, &pDescriptor);
			if (SUCCEEDED(hr))
			{
				IMFMediaTypeHandler *pMediaTypeHandler;
				hr = pDescriptor->GetMediaTypeHandler(&pMediaTypeHandler);
				if (SUCCEEDED(hr))
				{
					GUID guidMajorType;
					pMediaTypeHandler->GetMajorType(&guidMajorType);
					if (guidMajorType == MFMediaType_Audio)
					{
						if (i == idx)
							hr = pPD->SelectStream(i);
						else
							hr = pPD->DeselectStream(i);
					}

					pMediaTypeHandler->Release();
				}

				pDescriptor->Release();
			}
		}

		m_pSession->ClearTopologies();
		if (FAILED(hr))
			goto done;

		// Create a partial topology.
		hr = CreatePlaybackTopology(m_pSource, pPD, m_hwndVideo, &pTopology);

		if (FAILED(hr))
			goto done;

		// Set the topology on the media session.
		hr = m_pSession->SetTopology(MFSESSION_SETTOPOLOGY_IMMEDIATE, pTopology);
		//hr = m_pSession->SetTopology(0, pTopology);

		//if (FAILED(hr))
		//	goto done;

		if (FAILED(hr))
			goto done;

		////m_state = OpenPending;
	}

	//////////////
	PROPVARIANT var;
	PropVariantInit(&var);
	var.vt = VT_I8;
	var.hVal.QuadPart = time;

	if (m_state == Paused || m_state == Stopped)
		m_pRateControl->SetRate(FALSE, 0.0f);

	//{
	//	// Set the playback rate to zero without thinning.
	//	hr = m_pRateControl->SetRate(FALSE, 0.0f);
	//	hr = m_pSession->Start(NULL, &var);
	//	hr = m_pSession->Pause();
	//	hr = m_pRateControl->SetRate(FALSE, 1.0f);
	//}
	//else

	hr = m_pSession->Start(NULL, &var);

	//if (m_state == Paused)
	//	hr = m_pSession->Pause();

	// Clean up.
	PropVariantClear(&var);
	//////////////////////

done:
	SafeRelease(&pPD);
	SafeRelease(&pTopology);
	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::SelectVideoStream(DWORD idx)
{
	if (m_pSource == NULL)
		return E_UNEXPECTED;

	HRESULT hr = S_OK;

	IMFTopology *pTopology = NULL;
	IMFPresentationDescriptor *pPD = NULL;

	MFTIME time;
	GetTime(&time);

	if (m_state == Playing || m_state == Paused)
		m_pSession->Stop();

	hr = m_pSource->CreatePresentationDescriptor(&pPD);
	if (SUCCEEDED(hr))
	{
		DWORD cnt;
		BOOL selected;

		hr = pPD->GetStreamDescriptorCount(&cnt);
		if (FAILED(hr))
			goto done;

		for (DWORD i = 0; i < cnt; i++)
		{
			IMFStreamDescriptor *pDescriptor;
			hr = pPD->GetStreamDescriptorByIndex(i, &selected, &pDescriptor);
			if (SUCCEEDED(hr))
			{
				IMFMediaTypeHandler *pMediaTypeHandler;
				hr = pDescriptor->GetMediaTypeHandler(&pMediaTypeHandler);
				if (SUCCEEDED(hr))
				{
					GUID guidMajorType;
					pMediaTypeHandler->GetMajorType(&guidMajorType);
					if (guidMajorType == MFMediaType_Video)
					{
						if (i == idx)
							hr = pPD->SelectStream(i);
						else
							hr = pPD->DeselectStream(i);
					}

					pMediaTypeHandler->Release();
				}

				pDescriptor->Release();
			}
		}

		m_pSession->ClearTopologies();
		if (FAILED(hr))
			goto done;

		// Create a partial topology.
		hr = CreatePlaybackTopology(m_pSource, pPD, m_hwndVideo, &pTopology);

		if (FAILED(hr))
			goto done;

		// Set the topology on the media session.
		hr = m_pSession->SetTopology(MFSESSION_SETTOPOLOGY_IMMEDIATE, pTopology);

		if (FAILED(hr))
			goto done;

		////m_state = OpenPending;
	}

	//////////////
	PROPVARIANT var;
	PropVariantInit(&var);
	var.vt = VT_I8;
	var.hVal.QuadPart = time;

	if (m_state == Paused || m_state == Stopped)
		m_pRateControl->SetRate(FALSE, 0.0f);

	hr = m_pSession->Start(NULL, &var);

	PropVariantClear(&var);
	//////////////////////

done:
	SafeRelease(&pPD);
	SafeRelease(&pTopology);
	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::SetAspectRatioMode(DWORD mode)
{
    if (m_pVideoDisplay == NULL)
        return E_UNEXPECTED;

	return m_pVideoDisplay->SetAspectRatioMode(mode);
}

//######################################
//
//######################################
HRESULT CPlayer::SetFullscreen(BOOL fFullscreen)
{
    if (m_pVideoDisplay == NULL)
        return E_UNEXPECTED;

	return m_pVideoDisplay->SetFullscreen(fFullscreen);
}

//######################################
//
//######################################
HRESULT CPlayer::SetMute(BOOL bMute)
{
    if (m_pAudioVolume == NULL)
        return E_UNEXPECTED;
	return m_pAudioVolume->SetMute(bMute);
}

//######################################
//
//######################################
HRESULT CPlayer::SetProcAmpValue(DWORD dwProperty, float value)  // -1..1
{
	if (m_pVideoProcessor == NULL)
		return E_UNEXPECTED;

	DXVA2_ValueRange range;
	m_pVideoProcessor->GetProcAmpRange(dwProperty, &range);
	float DefaultValue = DXVA2FixedToFloat(range.DefaultValue);

	if (value < 0)
		value = DefaultValue + value * (DefaultValue - DXVA2FixedToFloat(range.MinValue));
	else
		value = DefaultValue + value * (DXVA2FixedToFloat(range.MaxValue) - DefaultValue);

	DXVA2_ProcAmpValues proc_amp_value;
	switch (dwProperty)
	{
	case DXVA2_ProcAmp_Brightness: proc_amp_value.Brightness = DXVA2FloatToFixed(value); break;
	case DXVA2_ProcAmp_Contrast: proc_amp_value.Contrast = DXVA2FloatToFixed(value); break;
	case DXVA2_ProcAmp_Hue: proc_amp_value.Hue = DXVA2FloatToFixed(value); break;
	case DXVA2_ProcAmp_Saturation: proc_amp_value.Saturation = DXVA2FloatToFixed(value); break;
	}

	m_pVideoProcessor->SetProcAmpValues(
		dwProperty,
		&proc_amp_value
	);
	return S_OK;
}

//######################################
// Sets the playback rate.
//######################################
HRESULT CPlayer::SetRate(float rate)
{
	if (m_pRateControl == NULL)
		return E_UNEXPECTED;

	return m_pRateControl->SetRate(FALSE, rate);
}

//######################################
//
//######################################
HRESULT CPlayer::SetTime(MFTIME time)
{
    if (m_pSession == NULL || m_pRateControl == NULL)
        return E_UNEXPECTED;

	PROPVARIANT var;
	PropVariantInit(&var);
	var.vt = VT_I8;
	var.hVal.QuadPart = time;
	HRESULT hr = m_pSession->Start(NULL, &var);
	PropVariantClear(&var);

	return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::SetVideoRect(RECT rcDest)
{
    if (m_pVideoDisplay)
        // Set the destination rectangle.
        // Leave the default source rectangle (0,0,1,1).
        return m_pVideoDisplay->SetVideoPosition(NULL, &rcDest);
    return S_OK;
}

//######################################
//
//######################################
HRESULT CPlayer::SetVolume(float fLevel)
{
    if (m_pAudioVolume == NULL)
        return E_UNEXPECTED;

	return m_pAudioVolume->SetMasterVolume(fLevel);
}

//######################################
//  Release all resources held by this object.
//######################################
HRESULT CPlayer::Shutdown()
{
    // Close the session
    HRESULT hr = CloseFile();

    // Shutdown the Media Foundation platform
    MFShutdown();

    if (m_hCloseEvent)
    {
        CloseHandle(m_hCloseEvent);
        m_hCloseEvent = NULL;
    }

    return hr;
}

//######################################
//
//######################################
HRESULT CPlayer::Stop()
{
    if (m_pSession == NULL)
        return E_UNEXPECTED;

    if (m_state != Playing && m_state != Paused)
        return MF_E_INVALIDREQUEST;

    HRESULT hr = m_pSession->Stop();
    if (SUCCEEDED(hr))
        m_state = Stopped;

    return hr;
}
