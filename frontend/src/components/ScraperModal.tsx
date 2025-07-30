// app/components/modals/ScraperModal.tsx
import React from 'react';
import { X, Link2 } from 'lucide-react';

interface ScraperModalProps {
  show: boolean;
  onClose: () => void;
}

const ScraperModal: React.FC<ScraperModalProps> = React.memo(({
  show,
  onClose,
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 p-4 bg-white/20 backdrop-blur-sm">
      <div className="bg-white rounded-3xl border-2 border-purple-500 p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Web Scraper</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Website URL</label>
            <div className="relative">
              <Link2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="url"
                placeholder="https://example.com"
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#3C04FC] focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Scraping Depth</label>
            <select className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#3C04FC] focus:border-transparent">
              <option>Current page only</option>
              <option>1 level deep</option>
              <option>2 levels deep</option>
              <option>3 levels deep</option>
            </select>
          </div>

          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Scraping Options</h4>
            <div className="space-y-2">
              <label className="flex items-center">
                <input type="checkbox" className="rounded mr-3" defaultChecked />
                <span className="text-sm text-gray-700">Extract main content only</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="rounded mr-3" />
                <span className="text-sm text-gray-700">Include images</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="rounded mr-3" defaultChecked />
                <span className="text-sm text-gray-700">Follow internal links</span>
              </label>
            </div>
          </div>
        </div>

        <div className="flex gap-4 mt-8">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button className="flex-1 bg-gradient-to-r from-[#3C04FC] to-[#BB4CD8] text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all">
            Start Scraping
          </button>
        </div>
      </div>
    </div>
  );
});

export default ScraperModal;