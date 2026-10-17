#include "Player.h"

CPlayer     *g_pPlayer = NULL;  // Global player object.

STDAPI Init(HWND hVideo, HWND hEvent)
{
	//HeapSetInformation(NULL, HeapEnableTerminationOnCorruption, NULL, 0);
	HRESULT hr = CPlayer::CreateInstance(hVideo, hEvent, &g_pPlayer);
	return hr;
}

STDAPI CloseFile()
{
	if (g_pPlayer)
		return g_pPlayer->CloseFile();
	return E_UNEXPECTED;
}

STDAPI GetAspectRatio(LPDWORD pRatio)
{
	if (g_pPlayer)
		return g_pPlayer->GetAspectRatio(pRatio);
	return E_UNEXPECTED;
}

STDAPI GetCapabilities(LPDWORD pCaps)
{
	if (g_pPlayer)
		return g_pPlayer->GetCapabilities(pCaps);
	return E_UNEXPECTED;
}

STDAPI GetCharacteristics(LPDWORD pCaps)
{
	if (g_pPlayer)
		return g_pPlayer->GetCharacteristics(pCaps);
	return E_UNEXPECTED;
}

STDAPI GetCurrentImage(BITMAPINFOHEADER *pBih, BYTE **pDib, DWORD *pcbDib, LONGLONG *pTimeStamp)
{
	if (g_pPlayer)
		return g_pPlayer->GetCurrentImage(pBih, pDib, pcbDib, pTimeStamp);
	return E_UNEXPECTED;
}

STDAPI GetDuration(MFTIME *pDur)
{
	if (g_pPlayer)
		return g_pPlayer->GetDuration(pDur);
	return E_UNEXPECTED;
}

STDAPI GetFrameRate(float *pfRate)
{
	if (g_pPlayer)
		return g_pPlayer->GetFrameRate(pfRate);
	return E_UNEXPECTED;
}

STDAPI GetMetadata(BYTE **pData, DWORD *pDataSize)
{
	if (g_pPlayer)
		return g_pPlayer->GetMetadata(pData, pDataSize);
	return E_UNEXPECTED;
}

STDAPI GetMute(BOOL *pbMute)
{
	if (g_pPlayer)
		return g_pPlayer->GetMute(pbMute);
	return E_UNEXPECTED;
}

STDAPI GetRate(float *pfRate)
{
	if (g_pPlayer)
		return g_pPlayer->GetRate(pfRate);
	return E_UNEXPECTED;
}

STDAPI GetSize(LPDWORD pSize)
{
	if (g_pPlayer)
		return g_pPlayer->GetSize(pSize);
	return E_UNEXPECTED;
}

STDAPI GetState(LPINT pState)
{
	if (g_pPlayer)
		return g_pPlayer->GetState((PlayerState*)pState);
	return E_UNEXPECTED;
}

STDAPI GetStream(DWORD idx, LPDWORD pType, LPDWORD pFourCC, LPBOOL pSelected, LPWSTR lang, size_t lang_buf_size)
{
	if (g_pPlayer)
		return g_pPlayer->GetStream(idx, pType, pFourCC, pSelected, lang, lang_buf_size);
	return E_UNEXPECTED;
}

STDAPI GetStreamCount(LPDWORD pCount)
{
	if (g_pPlayer)
		return g_pPlayer->GetStreamCount(pCount);
	return E_UNEXPECTED;
}

STDAPI GetTime(MFTIME *pTime)
{
	if (g_pPlayer)
		return g_pPlayer->GetTime(pTime);
	return E_UNEXPECTED;
}

STDAPI GetVolume(float *pfLevel)
{
	if (g_pPlayer)
		return g_pPlayer->GetVolume(pfLevel);
	return E_UNEXPECTED;
}

STDAPI HasAudio(LPBOOL pHasAudio)
{
	if (g_pPlayer)
		return g_pPlayer->HasAudio(pHasAudio);
	return E_UNEXPECTED;
}

STDAPI HasVideo(LPBOOL pHasVideo)
{
	if (g_pPlayer)
		return g_pPlayer->HasVideo(pHasVideo);
	return E_UNEXPECTED;
}

STDAPI LoadFile(LPCWSTR url)
{
	if (g_pPlayer)
		return g_pPlayer->LoadFile(url);
	return E_UNEXPECTED;
}

STDAPI Pause()
{
	if (g_pPlayer)
		return g_pPlayer->Pause();
	return E_UNEXPECTED;
}

STDAPI Play()
{
	if (g_pPlayer)
		return g_pPlayer->Play();
	return E_UNEXPECTED;
}

STDAPI Repaint()
{
    if (g_pPlayer)
		return g_pPlayer->Repaint();
	return E_UNEXPECTED;
}

STDAPI ResizeVideo(WORD width, WORD height)
{
	if (g_pPlayer)
		return g_pPlayer->ResizeVideo(width, height);
	return E_UNEXPECTED;
}

STDAPI SelectAudioStream(DWORD idx)
{
	if (g_pPlayer)
		return g_pPlayer->SelectAudioStream(idx);
	return E_UNEXPECTED;
}

STDAPI SelectVideoStream(DWORD idx)
{
	if (g_pPlayer)
		return g_pPlayer->SelectVideoStream(idx);
	return E_UNEXPECTED;
}

STDAPI SetAspectRatioMode(DWORD mode)
{
	if (g_pPlayer)
		return g_pPlayer->SetAspectRatioMode(mode);
	return E_UNEXPECTED;
}

STDAPI SetFullscreen(BOOL fFullscreen)
{
	if (g_pPlayer)
		return g_pPlayer->SetFullscreen(fFullscreen);
	return E_UNEXPECTED;
}

STDAPI SetMute(BOOL bMute)
{
	if (g_pPlayer)
		return g_pPlayer->SetMute(bMute);
	return E_UNEXPECTED;
}

STDAPI SetProcAmpValue(DWORD dwProperty, float value)
{
	if (g_pPlayer)
		return g_pPlayer->SetProcAmpValue(dwProperty, value);
	return E_UNEXPECTED;
}

STDAPI SetRate(float rate)
{
	if (g_pPlayer)
		return g_pPlayer->SetRate(rate);
	return E_UNEXPECTED;
}

STDAPI SetTime(MFTIME time)
{
	if (g_pPlayer)
		return g_pPlayer->SetTime(time);
	return E_UNEXPECTED;
}

STDAPI SetVideoRect(RECT rc)
{
	if (g_pPlayer)
		return g_pPlayer->SetVideoRect(rc);
	return E_UNEXPECTED;
}

STDAPI SetVolume(float fLevel)
{
	if (g_pPlayer)
		return g_pPlayer->SetVolume(fLevel);
	return E_UNEXPECTED;
}

STDAPI Shutdown()
{
	if (g_pPlayer)
		return g_pPlayer->Shutdown();
	return E_UNEXPECTED;
}

STDAPI Stop()
{
	if (g_pPlayer)
		return g_pPlayer->Stop();
	return E_UNEXPECTED;
}
