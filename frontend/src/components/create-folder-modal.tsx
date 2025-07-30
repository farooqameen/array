// app/components/modals/CreateFolderModal.tsx
import React from 'react';
import { X } from 'lucide-react';

interface CreateFolderModalProps {
  show: boolean;
  onClose: () => void;
  newKnowledgeBase: { name: string; description: string; category: string; };
  setNewKnowledgeBase: React.Dispatch<React.SetStateAction<{ name: string; description: string; category: string; }>>;
  onCreate: () => void;
}

const CreateFolderModal: React.FC<CreateFolderModalProps> = React.memo(({
  show,
  onClose,
  newKnowledgeBase,
  setNewKnowledgeBase,
  onCreate,
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 p-4 bg-white/20 backdrop-blur-sm">
      <div className="bg-white border-2 border-purple-500 rounded-3xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Create Knowledge Base</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Knowledge Base Name</label>
            <input
              type="text"
              placeholder="e.g., Financial Reports 2024"
              value={newKnowledgeBase.name}
              onChange={(e) => setNewKnowledgeBase(prev => ({ ...prev, name: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#3C04FC] focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              placeholder="Brief description of what this knowledge base contains..."
              rows={3}
              value={newKnowledgeBase.description}
              onChange={(e) => setNewKnowledgeBase(prev => ({ ...prev, description: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#3C04FC] focus:border-transparent resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={newKnowledgeBase.category}
              onChange={(e) => setNewKnowledgeBase(prev => ({ ...prev, category: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#3C04FC] focus:border-transparent"
            >
              <option value="">Select category...</option>
              <option value="finance">Finance</option>
              <option value="product">Product</option>
              <option value="marketing">Marketing</option>
              <option value="hr">Human Resources</option>
              <option value="documentation">Documentation</option>
              <option value="legal">Legal</option>
              <option value="operations">Operations</option>
            </select>
          </div>
        </div>

        <div className="flex gap-4 mt-8">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onCreate}
            disabled={!newKnowledgeBase.name.trim()}
            className="flex-1 bg-gradient-to-r from-[#3C04FC] to-[#BB4CD8] text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Create Knowledge Base
          </button>
        </div>
      </div>
    </div>
  );
});

export default CreateFolderModal;