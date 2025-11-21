import React, { useRef, useState, useEffect } from 'react';
import StatusBadge from './StatusBadge';

const CameraTile = ({ camera, onVideoUpload, onStatusChange }) => {
  const fileInputRef = useRef(null);
  const videoContainerRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [videoPreview, setVideoPreview] = useState(null);
  const [hasVideo, setHasVideo] = useState(false);
  const [streamUrl, setStreamUrl] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLiveCamera, setIsLiveCamera] = useState(false);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);
    
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
    };
  }, []);

  const handleUploadVideo = () => {
    fileInputRef.current?.click();
  };

  const handleStopVideo = async () => {
    console.log('Stop button clicked for', camera.id);
    
    // Call backend to cleanup video
    try {
      await fetch(`http://localhost:5000/api/stop_video/${camera.id}`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error stopping video:', error);
    }
    
    // Clear video preview and stream
    if (videoPreview) {
      URL.revokeObjectURL(videoPreview);
    }
    setVideoPreview(null);
    setStreamUrl(null);
    setHasVideo(false);
    setIsLiveCamera(false);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    // Set camera back to offline and reset stats
    if (onStatusChange) {
      onStatusChange(camera.id, 'offline', true);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('video', file);
      formData.append('camera_id', camera.id);

      console.log('Uploading video for detection:', camera.id, 'File size:', (file.size / 1024 / 1024).toFixed(2), 'MB');

      // Add timeout to the fetch request (2 minutes)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const response = await fetch('http://localhost:5000/api/detect', {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.msg || `Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Detection result:', result);
      
      // Display video stream with detection overlays
      if (result.stream_url) {
        const fullStreamUrl = `http://localhost:5000${result.stream_url}`;
        setStreamUrl(fullStreamUrl);
        setHasVideo(true);
        console.log('Starting video stream:', fullStreamUrl);
      }

      // Set camera to online after successful detection
      onStatusChange(camera.id, 'online');
      
      // Pass detection results to parent
      onVideoUpload(camera.id, result);

    } catch (error) {
      console.error('Error uploading video:', error);
      if (error.name === 'AbortError') {
        alert('Upload timeout - video processing took too long. Please try a shorter video.');
      } else {
        alert(`Failed to upload video: ${error.message}`);
      }
      handleStopVideo();
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleLiveCamera = async () => {
    try {
      setUploading(true);

      console.log(`Starting live camera for ${camera.id}`);

      const response = await fetch(`http://localhost:5000/api/start_live_camera/${camera.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          camera_index: 0  // Always use camera 0 (default webcam)
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start live camera: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Live camera started:', result);

      if (result.stream_url) {
        const fullStreamUrl = `http://localhost:5000${result.stream_url}`;
        setStreamUrl(fullStreamUrl);
        setHasVideo(true);
        setIsLiveCamera(true);
        console.log('Live camera stream:', fullStreamUrl);
      }

      onStatusChange(camera.id, 'online');

    } catch (error) {
      console.error('Error starting live camera:', error);
      alert(`Failed to start live camera: ${error.message}`);
      handleStopVideo();
    } finally {
      setUploading(false);
    }
  };

  const handleFullscreen = () => {
    if (!videoContainerRef.current) return;
    
    if (!isFullscreen) {
      // Enter fullscreen
      if (videoContainerRef.current.requestFullscreen) {
        videoContainerRef.current.requestFullscreen();
      } else if (videoContainerRef.current.webkitRequestFullscreen) {
        videoContainerRef.current.webkitRequestFullscreen();
      } else if (videoContainerRef.current.mozRequestFullScreen) {
        videoContainerRef.current.mozRequestFullScreen();
      } else if (videoContainerRef.current.msRequestFullscreen) {
        videoContainerRef.current.msRequestFullscreen();
      }
      setIsFullscreen(true);
    } else {
      // Exit fullscreen
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
      setIsFullscreen(false);
    }
  };

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-4">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="video/*"
        className="hidden"
      />
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white">{camera.name}</h3>
        </div>
        <StatusBadge status={camera.status} />
      </div>

      {/* Video Preview Area */}
      <div 
        ref={videoContainerRef}
        className="bg-dark-bg rounded-lg mb-4 aspect-video flex items-center justify-center border border-dark-border overflow-hidden relative group"
      >
        {streamUrl ? (
          <>
            <img
              src={streamUrl}
              alt={`${camera.name} live detection stream`}
              className="w-full h-full object-cover"
            />
            {/* Fullscreen button - shows on hover */}
            <button
              onClick={handleFullscreen}
              className="absolute top-2 right-2 bg-black/70 hover:bg-black/90 text-white p-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10"
              title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            >
              {isFullscreen ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              )}
            </button>
          </>
        ) : videoPreview ? (
          <video
            src={videoPreview}
            className="w-full h-full object-cover"
            controls
            autoPlay
            muted
            loop
          />
        ) : (
          <div className="text-center">
            <svg
              className="w-16 h-16 mx-auto mb-2 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            <p className="text-gray-500 text-sm">No video feed</p>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        {!hasVideo ? (
          <>
            <button
              onClick={handleUploadVideo}
              disabled={uploading}
              className={`${
                uploading 
                  ? 'bg-blue-400 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700'
              } text-white text-sm font-medium py-2 px-3 rounded transition-colors`}
            >
              {uploading ? '⏳ Processing...' : '📁 Upload Video'}
            </button>
            <button
              onClick={handleLiveCamera}
              disabled={uploading}
              className={`${
                uploading 
                  ? 'bg-green-400 cursor-not-allowed' 
                  : 'bg-green-600 hover:bg-green-700'
              } text-white text-sm font-medium py-2 px-3 rounded transition-colors`}
            >
              {uploading ? '⏳ Starting...' : '📹 Live Camera'}
            </button>
          </>
        ) : (
          <>
            {!isLiveCamera && (
              <button
                onClick={handleUploadVideo}
                disabled={uploading}
                className={`${
                  uploading 
                    ? 'bg-blue-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                } text-white text-sm font-medium py-2 px-3 rounded transition-colors`}
              >
                {uploading ? '⏳ Uploading...' : '🔄 Re-upload'}
              </button>
            )}
            <button
              onClick={handleStopVideo}
              disabled={uploading}
              className={`${!isLiveCamera ? '' : 'col-span-2'} bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white text-sm font-medium py-2 px-3 rounded transition-colors`}
            >
              ⏹️ Stop {isLiveCamera ? 'Camera' : 'Video'}
            </button>
          </>
        )}
      </div>

      {/* Stats - Hidden for live camera */}
      {!isLiveCamera && (
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-dark-bg rounded-lg p-3 border border-dark-border">
            <div className="text-xs text-gray-400 mb-1">Count</div>
            <div className="text-2xl font-bold text-white">{camera.count}</div>
          </div>
          <div className="bg-dark-bg rounded-lg p-3 border border-dark-border">
            <div className="text-xs text-gray-400 mb-1">Flow</div>
            <div className="text-2xl font-bold text-white">{camera.flow}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CameraTile;
