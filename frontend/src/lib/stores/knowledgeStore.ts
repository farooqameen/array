// stores/knowledgeStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Document {
  id: number;
  name: string;
  type: string;
  size: string;
  uploadDate: string;
  status: 'processing' | 'processed' | 'failed';
  pages: number;
  source: 'upload' | 'scrape';
  url?: string;
}

export interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
  category: string;
  documentsCount: number;
  scrapedPagesCount: number;
  createdDate: string;
  lastUpdated: string;
  documents: Document[];
}

interface KnowledgeState {
  knowledgeBases: KnowledgeBase[];
  addKnowledgeBase: (knowledgeBase: KnowledgeBase) => void;
  removeKnowledgeBase: (id: number) => void;
  updateKnowledgeBase: (id: number, updates: Partial<KnowledgeBase>) => void;
  addDocumentToKnowledgeBase: (knowledgeBaseId: number, document: Document) => void;
  removeDocumentFromKnowledgeBase: (knowledgeBaseId: number, documentId: number) => void;
  getTotalDocuments: () => number;
  getTotalScrapedPages: () => number;
  getKnowledgeBaseById: (id: number) => KnowledgeBase | undefined;
}

export const useKnowledgeStore = create<KnowledgeState>()(
  persist(
    (set, get) => ({
      knowledgeBases: [],

      addKnowledgeBase: (knowledgeBase) =>
        set((state) => ({
          knowledgeBases: [...state.knowledgeBases, knowledgeBase],
        })),

      removeKnowledgeBase: (id) =>
        set((state) => ({
          knowledgeBases: state.knowledgeBases.filter((kb) => kb.id !== id),
        })),

      updateKnowledgeBase: (id, updates) =>
        set((state) => ({
          knowledgeBases: state.knowledgeBases.map((kb) =>
            kb.id === id
              ? { ...kb, ...updates, lastUpdated: new Date().toISOString().split('T')[0] }
              : kb
          ),
        })),

      addDocumentToKnowledgeBase: (knowledgeBaseId, document) =>
        set((state) => ({
          knowledgeBases: state.knowledgeBases.map((kb) =>
            kb.id === knowledgeBaseId
              ? {
                  ...kb,
                  documents: [...kb.documents, document],
                  documentsCount: document.source === 'upload' 
                    ? kb.documentsCount + 1 
                    : kb.documentsCount,
                  scrapedPagesCount: document.source === 'scrape' 
                    ? kb.scrapedPagesCount + document.pages 
                    : kb.scrapedPagesCount,
                  lastUpdated: new Date().toISOString().split('T')[0],
                }
              : kb
          ),
        })),

      removeDocumentFromKnowledgeBase: (knowledgeBaseId, documentId) =>
        set((state) => ({
          knowledgeBases: state.knowledgeBases.map((kb) =>
            kb.id === knowledgeBaseId
              ? {
                  ...kb,
                  documents: kb.documents.filter((doc) => doc.id !== documentId),
                  documentsCount: kb.documents.filter((doc) => doc.id !== documentId && doc.source === 'upload').length,
                  scrapedPagesCount: kb.documents
                    .filter((doc) => doc.id !== documentId && doc.source === 'scrape')
                    .reduce((sum, doc) => sum + doc.pages, 0),
                  lastUpdated: new Date().toISOString().split('T')[0],
                }
              : kb
          ),
        })),

      getTotalDocuments: () => {
        const state = get();
        return state.knowledgeBases.reduce((total, kb) => total + kb.documentsCount, 0);
      },

      getTotalScrapedPages: () => {
        const state = get();
        return state.knowledgeBases.reduce((total, kb) => total + kb.scrapedPagesCount, 0);
      },

      getKnowledgeBaseById: (id) => {
        const state = get();
        return state.knowledgeBases.find((kb) => kb.id === id);
      },
    }),
    {
      name: 'knowledge-base-storage', // name of the item in localStorage
      // Only persist the knowledge bases data
      partialize: (state) => ({ knowledgeBases: state.knowledgeBases }),
    }
  )
);