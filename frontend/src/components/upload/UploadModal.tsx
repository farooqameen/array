import React from 'react';
import { X, Upload } from 'lucide-react';

interface UploadModalProps {
  show: boolean;
  onClose: () => void;
  selectedFolderId: number | null;
  onFileUpload: (files: File[], knowledgeBaseId: number) => void;
  uploadingFiles: File[];
  uploadProgress: Record<string, number>;
}

const UploadModal: React.FC<UploadModalProps> = React.memo(({
  show,
  onClose,
  selectedFolderId,
  onFileUpload,
  uploadingFiles,
  uploadProgress,
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 p-4 bg-white/20 backdrop-blur-sm">
      <div className="bg-white rounded-3xl border-2 border-purple-500 p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Upload Documents</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center hover:border-[#3C04FC] transition-colors">
          <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Drop files here or click to browse</h3>
          <p className="text-gray-600 mb-6">Support for PDF, DOCX, PPTX, TXT, XLSX files up to 50MB</p>

          <input
            type="file"
            multiple
            accept=".pdf,.docx,.pptx,.txt,.xlsx"
            onChange={(e) => {
              if (e.target.files && selectedFolderId) {
                const filesArray = Array.from(e.target.files);
                onFileUpload(filesArray, selectedFolderId);
              } else if (!selectedFolderId) {
                alert("Please select a knowledge base first to upload documents.");
              }
            }}
            className="hidden"
            id="file-upload"
          />

          <label
            htmlFor="file-upload"
            className="bg-gradient-to-r from-[#3C04FC] to-[#BB4CD8] text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all cursor-pointer inline-block"
          >
            Choose Files
          </label>
        </div>

        {/* Upload Progress */}
        {uploadingFiles.length > 0 && (
          <div className="mt-6 space-y-3">
            <h4 className="font-semibold text-gray-900">Uploading Files...</h4>
            {uploadingFiles.map((file) => (
              <div key={file.name} className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">{file.name}</span>
                  <span className="text-xs text-gray-600">
                    {uploadProgress[file.name] === -1 ? 'Failed' :
                     uploadProgress[file.name] === 100 ? 'Complete' :
                     `${uploadProgress[file.name] || 0}%`}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      uploadProgress[file.name] === -1 ? 'bg-red-500' :
                      uploadProgress[file.name] === 100 ? 'bg-green-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.max(uploadProgress[file.name] || 0, 10)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-4 mt-8">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
});

export default UploadModal;