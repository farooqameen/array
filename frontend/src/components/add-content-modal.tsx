// app/components/modals/AddContentModal.tsx
import React from 'react';
import { X, Upload, Globe, ChevronRight } from 'lucide-react';

interface AddContentModalProps {
  show: boolean;
  onClose: () => void;
  onShowUploadModal: () => void;
  onShowScraperModal: () => void;
}

const AddContentModal: React.FC<AddContentModalProps> = React.memo(({
  show,
  onClose,
  onShowUploadModal,
  onShowScraperModal,
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 p-4 bg-white/20 backdrop-blur-sm">
      <div className="bg-white rounded-3xl border-2 border-purple-500 p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Add Content to Knowledge Base</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="text-center mb-8">
          <p className="text-lg text-gray-600">Choose how you want to add content to your knowledge base</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <button
            onClick={onShowUploadModal}
            className="group bg-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#3C04FC] hover:shadow-lg transition-all transform hover:scale-105"
          >
            <div className="w-16 h-16 bg-gradient-to-r from-[#3C04FC] to-[#230197] rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:shadow-xl transition-all">
              <Upload className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">Upload Documents</h3>
            <p className="text-gray-600 leading-relaxed">
              Upload PDFs, Word docs, spreadsheets, and other files to your knowledge base
            </p>
            <div className="flex items-center justify-center text-[#3C04FC] font-semibold text-sm mt-6 group-hover:translate-x-1 transition-transform">
              Choose Files <ChevronRight className="w-4 h-4 ml-1" />
            </div>
          </button>

          <button
            onClick={onShowScraperModal}
            className="group bg-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#BB4CD8] hover:shadow-lg transition-all transform hover:scale-105"
          >
            <div className="w-16 h-16 bg-gradient-to-r from-[#BB4CD8] to-[#671B7D] rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:shadow-xl transition-all">
              <Globe className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">Web Scraper</h3>
            <p className="text-gray-600 leading-relaxed">
              Scrape content from websites and automatically add it to your knowledge base
            </p>
            <div className="flex items-center justify-center text-[#BB4CD8] font-semibold text-sm mt-6 group-hover:translate-x-1 transition-transform">
              Start Scraping <ChevronRight className="w-4 h-4 ml-1" />
            </div>
          </button>
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={onClose}
            className="px-6 py-3 text-gray-600 hover:text-gray-800 transition-colors"
          >
            I'll add content later
          </button>
        </div>
      </div>
    </div>
  );
});

export default AddContentModal;