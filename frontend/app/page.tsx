"use client";

import React, { useState } from 'react';

// Define the shape of our prediction result
interface PredictionResult {
  className: string;
  confidence: string;
}

export default function App() {
  // Add TypeScript generics to useState hooks
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // The URL to your FastAPI backend
  const API_URL = 'http://localhost:8000/predict'; 

  // Handle when the user selects an image with proper React event typing
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Safely access the files array
    const file = e.target.files?.[0];
    setResult(null);
    setError(null);
    
    if (file) {
      setImageFile(file);
      // Generate a local preview of the uploaded image
      const reader = new FileReader();
      reader.onload = (event) => {
        // Cast the result to a string for the image src
        setPreviewUrl(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setImageFile(null);
      setPreviewUrl(null);
    }
  };

  // Handle clicking the Predict button
  const handlePredict = async () => {
    if (!imageFile) return;

    setIsLoading(true);
    setResult(null);
    setError(null);

    // Prepare the file for FastAPI
    const formData = new FormData();
    formData.append('file', imageFile);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      
      // Parse the response from your FastAPI backend
      const foodClass: string = data.class || data.prediction || "Unknown";
      let confidence: number = data.confidence || data.score || 0;
      
      // Convert 0.98 format to 98.0 format if necessary
      if (confidence <= 1.0) {
        confidence = confidence * 100;
      }

      // Format the result for the UI
      setResult({
        className: foodClass.replace(/_/g, ' '),
        confidence: confidence.toFixed(1)
      });
      
    } catch (err) {
      console.error('API Error:', err);
      setError("Unable to connect to the backend API. Ensure FastAPI is running and CORS is allowed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex items-center justify-center p-6 md:p-12 font-sans">
      <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2 gap-12 lg:gap-24 items-stretch">
        
        {/* =========================================
            LEFT COMPONENT: Upload Card
            ========================================= */}
        <div className="bg-white rounded-3xl shadow-lg border border-slate-100 p-8 flex flex-col h-full min-h-125 relative z-10">
          
          <div className="mb-6">
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 mb-2">FoodVision AI</h1>
            <p className="text-slate-500">Upload a photo of your meal to identify it.</p>
          </div>

          {/* Upload Dropzone */}
          <div className="relative group cursor-pointer grow flex flex-col mb-6">
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleImageChange}
              aria-label="Upload food image"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
            />
            <div className={`grow border-2 border-dashed rounded-2xl flex flex-col items-center justify-center p-6 transition-all duration-200 overflow-hidden ${previewUrl ? 'border-blue-400 bg-blue-50/30' : 'border-slate-300 bg-slate-50 group-hover:bg-slate-100 group-hover:border-blue-400'}`}>
              
              {!previewUrl ? (
                <div className="flex flex-col items-center text-center">
                  <div className="w-16 h-16 bg-white rounded-full shadow-sm flex items-center justify-center mb-4 text-blue-500 group-hover:scale-110 transition-transform">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                  </div>
                  <p className="text-base font-semibold text-slate-700">Click or drag image here</p>
                  <p className="text-sm text-slate-400 mt-1">Supports JPG, PNG up to 5MB</p>
                </div>
              ) : (
                <img src={previewUrl} className="w-full h-full object-cover rounded-xl shadow-sm" alt="Selected food" />
              )}
            </div>
          </div>

          {/* Predict Button */}
          <button 
            onClick={handlePredict}
            disabled={!imageFile || isLoading} 
            className="w-full bg-blue-600 text-white text-lg font-bold py-4 px-6 rounded-2xl shadow-md hover:bg-blue-700 hover:shadow-lg focus:outline-none focus:ring-4 focus:ring-blue-500/50 disabled:opacity-60 disabled:hover:bg-blue-600 disabled:cursor-not-allowed transition-all flex justify-center items-center gap-3 mt-auto"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white/20 border-t-white"></div>
                Analyzing Image...
              </>
            ) : (
              'Predict Food'
            )}
          </button>
        </div>

        {/* =========================================
            RIGHT COMPONENT: Borderless Results Area
            ========================================= */}
        <div className="flex flex-col justify-center p-4 md:p-8 h-full">
          
          {/* State 1: Awaiting Input */}
          {!isLoading && !result && !error && (
            <div className="text-slate-400 space-y-4 animate-pulse opacity-60">
              <div className="w-16 h-16 rounded-full bg-slate-200 mb-6"></div>
              <div className="h-4 bg-slate-200 rounded w-3/4"></div>
              <div className="h-4 bg-slate-200 rounded w-1/2"></div>
              <p className="pt-8 text-lg font-medium text-slate-400">Awaiting image upload...</p>
            </div>
          )}

          {/* State 2: Error */}
          {error && (
            <div className="text-red-500 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <svg className="w-16 h-16 mb-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              <h2 className="text-2xl font-bold mb-2">Connection Failed</h2>
              <p className="text-red-400/80">{error}</p>
            </div>
          )}

          {/* State 3: Loading */}
          {isLoading && (
            <div className="text-blue-600 space-y-4 animate-in fade-in duration-300">
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-6"></div>
              <h2 className="text-3xl font-bold text-slate-800 animate-pulse">Consulting the AI...</h2>
              <p className="text-slate-500">Scanning ingredients and textures.</p>
            </div>
          )}

          {/* State 4: Final Result */}
          {result && !isLoading && (
            <div className="transform transition-all duration-500 translate-y-0 opacity-100 animate-in slide-in-from-left-8 fade-in">
              <p className="text-sm font-bold tracking-widest text-blue-500 uppercase mb-3">Prediction Result</p>
              
              <h2 className="text-5xl lg:text-7xl font-black text-slate-900 capitalize leading-tight mb-6 tracking-tight">
                {result.className}
              </h2>
              
              <div className="inline-flex items-center gap-3 bg-white/60 backdrop-blur-md border border-slate-200 shadow-sm px-6 py-3 rounded-full">
                <span className="flex h-3 w-3 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                </span>
                <p className="text-slate-700 font-medium">
                  <span className="text-emerald-600 font-bold text-xl mr-1">{result.confidence}%</span> 
                  Confidence
                </p>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
