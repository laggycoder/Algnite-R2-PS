import React, { useState } from 'react';
import type { ChangeEvent } from 'react';
import { UploadCloud } from 'lucide-react';

interface ImageUploadProps {
  onImageUpload: (file: File) => void;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onImageUpload }) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('No file chosen');

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setPreview(URL.createObjectURL(file));
      setFileName(file.name);
      onImageUpload(file);
    } else {
      setPreview(null);
      setFileName('No file chosen');
    }
  };

  return (
    <div className="image-upload-area section">
      <h2><UploadCloud size={22} />Upload Your Image</h2>
      <input 
        type="file" 
        id="imageUploadInput" 
        accept="image/*" 
        onChange={handleFileChange} 
        aria-label="Upload image file"
      />
      {/* Visually hidden label for accessibility or custom styled trigger
      <label htmlFor="imageUploadInput" className="custom-file-upload-button">
        Choose File ({fileName})
      </label> 
      */}
      <div className="image-preview-container">
        {preview ? (
          <img src={preview} alt="Preview" className="image-preview" />
        ) : (
          <p style={{ color: '#7f8c8d', textAlign: 'center' }}>Image preview will appear here</p>
        )}
      </div>
    </div>
  );
};

export default ImageUpload;
