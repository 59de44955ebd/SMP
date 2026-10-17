#ifndef PLAYER_H
#define PLAYER_H

#include <new>
#include <windows.h>
#include <shobjidl.h>
#include <shlwapi.h>
#include <assert.h>

// Media Foundation headers
#include <mfapi.h>
#include <mfidl.h>
#include <mferror.h>
#include <d3d9.h>
#include <evr9.h>

#include <propkey.h>

#include "resource.h"

template <class T> void SafeRelease(T **ppT)
{
    if (*ppT)
    {
        (*ppT)->Release();
        *ppT = NULL;
    }
}

const UINT WM_APP_PLAYER_EVENT = WM_APP + 1;

enum PlayerState
{
    Closed = 0,     // No session.
    Ready,          // Session was created, ready to open a file.
    OpenPending,    // Session is opening a file.
    Playing,        // Session is playing a file.
    Paused,         // Session is paused.
    Stopped,        // Session is stopped (ready to play).
    Closing         // Application has closed the session, but is waiting for MESessionClosed.
};

HRESULT CreateMediaSource(PCWSTR pszURL, IMFMediaSource **ppSource);

HRESULT CreatePlaybackTopology(IMFMediaSource *pSource,
    IMFPresentationDescriptor *pPD, HWND hVideoWnd, IMFTopology **ppTopology);

class CPlayer : public IMFAsyncCallback
{
public:
    static HRESULT CreateInstance(HWND hVideo, HWND hEvent, CPlayer **ppPlayer);

    // IUnknown methods
    STDMETHODIMP QueryInterface(REFIID iid, void** ppv);
    STDMETHODIMP_(ULONG) AddRef();
    STDMETHODIMP_(ULONG) Release();

    // IMFAsyncCallback methods
    STDMETHODIMP  GetParameters(DWORD*, DWORD*)
    {
        // Implementation of this method is optional.
        return E_NOTIMPL;
    }
    STDMETHODIMP  	Invoke(IMFAsyncResult* pAsyncResult);

	HRESULT		CloseFile();
	HRESULT		GetAspectRatio(LPDWORD pRatio);
	HRESULT		GetCapabilities(LPDWORD);
	HRESULT		GetCharacteristics(LPDWORD);
	HRESULT		GetCurrentImage(BITMAPINFOHEADER *pBih, BYTE **pDib, DWORD *pcbDib, LONGLONG *pTimeStamp);
	HRESULT		GetDuration(MFTIME *pDuration);
	HRESULT		GetFrameRate(float *pfRate);
	HRESULT		GetMetadata(BYTE **pData, DWORD *pDataSize);
	HRESULT		GetMute(LPBOOL pbMute);
	HRESULT		GetRate(float *pfRate);
	HRESULT		GetSize(LPDWORD pSize);
	HRESULT		GetState(PlayerState *pState);
	HRESULT		GetStream(DWORD idx, LPDWORD pType, LPDWORD pFourCC, LPBOOL pSelected, LPWSTR lang, size_t lang_buf_size);
	HRESULT		GetStreamCount(LPDWORD pCount);
	HRESULT		GetTime(MFTIME *phnsTime);
	HRESULT		GetVolume(float *pfLevel);
	HRESULT		HasAudio(LPBOOL pHasAudio);
	HRESULT		HasVideo(LPBOOL pHasVideo);
	HRESULT		LoadFile(const WCHAR *sURL);
	HRESULT		Pause();
	HRESULT		Play();
	HRESULT		Repaint();
	HRESULT		ResizeVideo(WORD width, WORD height);
	HRESULT		SelectAudioStream(DWORD idx);
	HRESULT		SelectVideoStream(DWORD idx);
	HRESULT		SetAspectRatioMode(DWORD mode);
	HRESULT		SetFullscreen(BOOL fFullscreen);
	HRESULT		SetMute(BOOL bMute);
	HRESULT		SetProcAmpValue(DWORD dwProperty, float value);
	HRESULT		SetRate(float fRate);
	HRESULT		SetTime(MFTIME time);
	HRESULT		SetVideoRect(RECT rcDest);
	HRESULT		SetVolume(float fLevel);
	HRESULT		Shutdown();
	HRESULT		Stop();

protected:

    // Constructor is private. Use static CreateInstance method to instantiate.
    CPlayer(HWND hVideo, HWND hEvent);

    // Destructor is private. Caller should call Release.
    virtual ~CPlayer();

    HRESULT		Initialize();
    HRESULT		CreateSession();
    HRESULT		HandleEvent(UINT_PTR pUnkPtr);

    // Media event handlers
    virtual HRESULT OnTopologyStatus(IMFMediaEvent *pEvent);
    virtual HRESULT OnPresentationEnded(IMFMediaEvent *pEvent);
    virtual HRESULT OnNewPresentation(IMFMediaEvent *pEvent);

protected:
    long                    m_nRefCount;        // Reference count.

    IMFMediaSession         *m_pSession;
    IMFMediaSource          *m_pSource;
    IMFVideoDisplayControl  *m_pVideoDisplay;
	IMFSimpleAudioVolume    *m_pAudioVolume;
	IMFRateControl			*m_pRateControl;
	IMFPresentationClock	*m_pPresentationClock;
	IMFVideoProcessor		*m_pVideoProcessor;

    HWND                    m_hwndVideo;        // Video window.
    HWND                    m_hwndEvent;        // App window to receive events.

    PlayerState             m_state;            // Current state of the media session.
    HANDLE                  m_hCloseEvent;      // Event to wait on while closing.
};

#endif PLAYER_H
