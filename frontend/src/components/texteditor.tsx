"use client";
import React, { useState, useRef, useCallback, useEffect, useMemo, memo } from 'react';
import {
  Save, X, Plus, Trash2, Edit3, Calendar, Link2, Tag,
  ChevronDown, ChevronRight, FileText, Hash, Type,
  Copy, MoreVertical, Eye, EyeOff, Settings, Code, UploadCloud, DownloadCloud,
  LayoutPanelLeft, CheckCircle2, AlertCircle, Search, Filter, FolderTree,
  RefreshCw, Clock, User, Shield, FileJson, Move, Loader2
} from 'lucide-react';

// Utility function to generate unique IDs
const generateId = () => Math.random().toString(36).substr(2, 9);

// Reusable Button Component
type IconButtonProps = React.PropsWithChildren<{
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  className?: string;
  tooltip?: string;
  disabled?: boolean;
  [key: string]: any;
}>;

const IconButton = ({ children, onClick, className = "", tooltip = "", disabled = false, ...props }: IconButtonProps) => (
  <button
    onClick={onClick}
    className={`p-1 hover:bg-gray-100 rounded-md transition-colors ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    title={tooltip}
    disabled={disabled}
    {...props}
  >
    {children}
  </button>
);

// Reusable Input Field Component
type LabeledInputProps = {
  label: string;
  type?: string;
  value: string | number;
  onChange: React.ChangeEventHandler<HTMLInputElement | HTMLTextAreaElement>;
  placeholder?: string;
  className?: string;
  error?: string;
  inputKey?: string;
  onBlur?: React.FocusEventHandler<HTMLInputElement | HTMLTextAreaElement>; // Added onBlur prop
  onKeyPress?: React.KeyboardEventHandler<HTMLInputElement | HTMLTextAreaElement>; // Added onKeyPress prop
};

const LabeledInput = ({
  label,
  type = "text",
  value,
  onChange,
  placeholder = "",
  className = "",
  error = "",
  inputKey,
  onBlur,
  onKeyPress
}: LabeledInputProps) => {
  const InputComponent = type === "textarea" ? "textarea" : "input";
  return (
    <div>
      <label className="block text-xs font-medium text-gray-700 mb-1">{label}</label>
      <InputComponent
        key={inputKey}
        type={type === "textarea" ? undefined : type}
        value={value}
        onChange={onChange}
        onBlur={onBlur} // Pass onBlur to the input element
        onKeyPress={onKeyPress} // Pass onKeyPress to the input element
        placeholder={placeholder}
        className={`w-full p-2 text-sm border ${error ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:ring-2 focus:ring-[#3C04FC] focus:border-transparent ${className} ${type === "textarea" ? "min-h-[60px] resize-y" : ""}`}
      />
      {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    </div>
  );
};

// Category Management Component
type CategoryManagerProps = {
  categories?: string[];
  onAdd: (category: string) => void;
  onRemove: (category: string) => void;
  suggestions?: string[];
};

const CategoryManager = ({
  categories = [],
  onAdd,
  onRemove,
  suggestions = [],
}: CategoryManagerProps) => {
  const [isAdding, setIsAdding] = useState(false);
  const [newCategory, setNewCategory] = useState("");

  const handleAdd = () => {
    if (newCategory.trim() && !categories.includes(newCategory.trim())) {
      onAdd(newCategory.trim());
      setNewCategory("");
      setIsAdding(false);
    }
  };

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-2">
        <label className="block text-xs font-medium text-gray-700">Categories</label>
        <IconButton onClick={() => setIsAdding(true)} tooltip="Add new category">
          <Plus className="w-3 h-3 text-[#3C04FC]" />
        </IconButton>
      </div>
      
      {isAdding && (
        <div className="flex items-center gap-2 mb-2">
          <input
            type="text"
            value={newCategory}
            onChange={(e) => setNewCategory(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
            placeholder="Enter category name"
            className="flex-1 p-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-[#3C04FC]"
            autoFocus
          />
          <IconButton onClick={handleAdd} className="text-green-600">
            <CheckCircle2 className="w-4 h-4" />
          </IconButton>
          <IconButton onClick={() => { setIsAdding(false); setNewCategory(""); }} className="text-red-600">
            <X className="w-4 h-4" />
          </IconButton>
        </div>
      )}

      <div className="flex flex-wrap gap-1">
        {categories.map((category, index) => (
          <span
            key={index}
            className="inline-flex items-center px-2 py-1 bg-gradient-to-r from-[#3C04FC]/10 to-[#BB4CD8]/10 text-[#3C04FC] text-xs rounded-full border border-[#3C04FC]/20"
          >
            {category}
            <IconButton onClick={() => onRemove(category)} className="ml-1 hover:text-red-600">
              <X className="w-3 h-3" />
            </IconButton>
          </span>
        ))}
      </div>
    </div>
  );
};

// Custom Field Management Component
type CustomFieldManagerProps = {
  customFields?: Record<string, string>;
  onAdd: (key: string, value: string) => void;
  onUpdate: (oldKey: string, newKey: string, value: string) => void;
  onDelete: (key: string) => void;
};

const CustomFieldManager = ({
  customFields = {},
  onAdd,
  onUpdate,
  onDelete,
}: CustomFieldManagerProps) => {
  const [isAdding, setIsAdding] = useState(false);
  const [newField, setNewField] = useState({ key: '', value: '' });
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editingValue, setEditingValue] = useState<string>(''); // Local state for the value being edited

  // Sync local editing value with prop when editingField changes
  useEffect(() => {
    if (editingField && customFields[editingField]) {
      setEditingValue(customFields[editingField]);
    } else {
      setEditingValue('');
    }
  }, [editingField, customFields]);

  const handleAdd = () => {
    if (newField.key.trim() && newField.value.trim() && !customFields[newField.key.trim()]) {
      onAdd(newField.key.trim(), newField.value.trim());
      setNewField({ key: '', value: '' });
      setIsAdding(false);
    }
  };

  const handleLocalEditChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditingValue(e.target.value);
  };

  const handleEditBlur = (key: string) => {
    if (editingValue !== customFields[key]) {
      onUpdate(key, key, editingValue); // Update with the local editingValue
    }
    setEditingField(null); // Exit editing mode
  };

  const handleEditKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur(); // Trigger blur to save changes
    }
  };

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-2">
        <label className="block text-xs font-medium text-gray-700">Custom Fields</label>
        <IconButton onClick={() => setIsAdding(true)} tooltip="Add new custom field">
          <Plus className="w-3 h-3 text-[#3C04FC]" />
        </IconButton>
      </div>

      {isAdding && (
        <div className="flex items-center gap-2 mb-2">
          <input
            type="text"
            value={newField.key}
            onChange={(e) => setNewField({ ...newField, key: e.target.value })}
            placeholder="Field name"
            className="flex-1 p-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-[#3C04FC]"
          />
          <input
            type="text"
            value={newField.value}
            onChange={(e) => setNewField({ ...newField, value: e.target.value })}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
            placeholder="Field value"
            className="flex-1 p-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-[#3C04FC]"
          />
          <IconButton onClick={handleAdd} className="text-green-600">
            <CheckCircle2 className="w-4 h-4" />
          </IconButton>
          <IconButton onClick={() => { setIsAdding(false); setNewField({ key: '', value: '' }); }} className="text-red-600">
            <X className="w-4 h-4" />
          </IconButton>
        </div>
      )}

      <div className="space-y-2">
        {Object.entries(customFields).map(([key, value]) => (
          <div key={key} className="flex items-center space-x-2">
            {editingField === key ? (
              <>
                <input
                  type="text"
                  value={key}
                  disabled
                  className="flex-1 p-1 text-xs border border-gray-300 rounded bg-gray-100"
                />
                <input
                  key={`custom-field-edit-${key}-value`} // Add key for stability during editing
                  type="text"
                  value={editingValue} // Use local editingValue
                  onChange={handleLocalEditChange} // Update local state on change
                  onBlur={() => handleEditBlur(key)} // Save on blur
                  onKeyPress={handleEditKeyPress} // Save on Enter
                  className="flex-1 p-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-[#3C04FC]"
                  autoFocus
                />
                {/* The CheckCircle2 button now just exits editing mode, as saving is handled by blur/enter */}
                <IconButton onClick={() => handleEditBlur(key)} className="text-green-600">
                  <CheckCircle2 className="w-3 h-3" />
                </IconButton>
              </>
            ) : (
              <>
                <div className="flex-1 p-1 text-xs bg-gray-50 rounded">
                  <span className="font-medium">{key}:</span> {value}
                </div>
                <IconButton onClick={() => setEditingField(key)} className="hover:text-blue-600">
                  <Edit3 className="w-3 h-3" />
                </IconButton>
                <IconButton onClick={() => onDelete(key)} className="hover:text-red-600">
                  <Trash2 className="w-3 h-3" />
                </IconButton>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// --- Draggable Color Legend Component ---
type DraggableColorLegendProps = {
  sections: SectionNode[];
  sectionColors: { [id: string]: string };
  setSelectedSectionId: (id: string | null) => void;
  getAllSectionsFlat: (nodes: SectionNode[]) => SectionNode[];
  parentRef: React.RefObject<HTMLDivElement | null>;
};

// Define SectionNode type
type CustomFields = {
  [key: string]: string;
};

type SectionNode = {
  id: string;
  title: string;
  categories: string[];
  startPosition: number;
  endPosition: number;
  customFields: CustomFields;
  children: SectionNode[];
  highlightedContent?: string;
};

const DraggableColorLegend: React.FC<DraggableColorLegendProps> = ({ 
  sections, 
  sectionColors, 
  setSelectedSectionId, 
  getAllSectionsFlat,
  parentRef
}) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartOffset, setDragStartOffset] = useState({ x: 0, y: 0 });
  const legendRef = useRef<HTMLDivElement>(null);

  // Initialize position to top-right corner on mount
  useEffect(() => {
    if (parentRef.current && legendRef.current) {
      const parentRect = parentRef.current.getBoundingClientRect();
      const legendRect = legendRef.current.getBoundingClientRect();
      setPosition({
        x: parentRect.width - legendRect.width - 16, // 16px padding
        y: 16
      });
    }
  }, [parentRef]);

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    e.preventDefault(); // Prevent default browser action (like text selection)
    if (legendRef.current) {
      setIsDragging(true);
      const legendRect = legendRef.current.getBoundingClientRect();
      setDragStartOffset({
        x: e.clientX - legendRect.left,
        y: e.clientY - legendRect.top
      });
      // Add a class to body to prevent text selection during drag
      document.body.style.userSelect = 'none';
    }
  };

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    // Remove the style to re-enable text selection
    document.body.style.userSelect = '';
  }, []);
  
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging && parentRef.current) {
      const parentRect = parentRef.current.getBoundingClientRect();
      let newX = e.clientX - parentRect.left - dragStartOffset.x;
      let newY = e.clientY - parentRect.top - dragStartOffset.y;

      // Constrain movement within the parent boundaries
      if (legendRef.current) {
          const legendRect = legendRef.current.getBoundingClientRect();
          newX = Math.max(0, Math.min(newX, parentRect.width - legendRect.width));
          newY = Math.max(0, Math.min(newY, parentRect.height - legendRect.height));
      }

      setPosition({ x: newX, y: newY });
    }
  }, [isDragging, dragStartOffset, parentRef]);


  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    } else {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      document.body.style.userSelect = ''; // Clean up on unmount
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);
  
  return (
    <div
      ref={legendRef}
      className="absolute bg-white/80 backdrop-blur-sm border border-gray-200 rounded-lg shadow-lg p-3 max-w-xs z-20"
      style={{ top: `${position.y}px`, left: `${position.x}px` }}
    >
      <div 
        className="flex items-center justify-between mb-2 cursor-move"
        onMouseDown={handleMouseDown}
      >
        <h4 className="text-xs font-semibold text-gray-700">Section Colors</h4>
        <Move className="w-4 h-4 text-gray-400" />
      </div>
      <div className="space-y-1 max-h-40 overflow-y-auto">
        {getAllSectionsFlat(sections)
          .filter(s => s.startPosition < s.endPosition)
          .map(section => (
            <div 
              key={section.id} 
              className="flex items-center gap-2 text-xs cursor-pointer hover:bg-gray-50 p-1 rounded"
              onClick={() => setSelectedSectionId(section.id)}
            >
              <div 
                className="w-3 h-3 rounded flex-shrink-0" 
                style={{ backgroundColor: sectionColors[section.id] }}
              />
              <span className="truncate">{section.title}</span>
            </div>
          ))}
      </div>
    </div>
  );
};

// Define DocumentData type
interface DocumentData {
  id: string;
  title: string;
  description: string;
  categories: string[];
  sourceUrl: string;
  dateCreated: string;
  dateModified: string;
  author: string;
  version: string;
  tags: string[];
  customFields: CustomFields;
}

// Define the shape of the data expected from the fetch call
interface FetchedDocumentData {
  document: DocumentData;
  content: string;
  sections: SectionNode[];
}

// Props for DocumentEditor
interface DocumentEditorProps {
  filename?: string; // Optional filename prop
}

const DocumentEditor: React.FC<DocumentEditorProps> = ({ filename }) => {
  // Initial state with empty values, will be populated by fetch
  const [docData, setDocData] = useState<DocumentData>({
    id: generateId(),
    title: "",
    description: "",
    categories: [],
    sourceUrl: "",
    dateCreated: "",
    dateModified: "",
    author: "",
    version: "",
    tags: [],
    customFields: {}
  });

  // Content state - separate from document metadata
  const [content, setContent] = useState("");
  const [sections, setSections] = useState<SectionNode[]>([]);
  const [isLoading, setIsLoading] = useState(true); // Loading state

  // --- Fetch data on component mount or filename change ---
  useEffect(() => {
    const fetchData = async () => {
      if (!filename) {
        setIsLoading(false);
        return; // If no filename, don't fetch
      }

      setIsLoading(true);
      try {
        const response = await fetch(`http://localhost:8000/getjson/${filename}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: FetchedDocumentData = await response.json();
        
        // Populate state with fetched data
        setDocData(data.document);
        setContent(data.content || ''); // Ensure content is not null/undefined
        
        // Sanitize sections by removing 'highlightedContent' if present
        const sanitizedSections = data.sections.map((section: SectionNode) => {
          const newSection = { ...section };
          delete newSection.highlightedContent;
          if (newSection.children && newSection.children.length > 0) {
            const sanitizeChildren = (nodes: SectionNode[]): SectionNode[] => {
              return nodes.map((childNode: SectionNode) => {
                const newChildNode = { ...childNode };
                delete newChildNode.highlightedContent;
                if (newChildNode.children && newChildNode.children.length > 0) {
                  newChildNode.children = sanitizeChildren(newChildNode.children);
                }
                return newChildNode;
              });
            };
            newSection.children = sanitizeChildren(newSection.children);
          }
          return newSection;
        });
        setSections(sanitizedSections);

        // Expand all imported sections
        const allIds = getAllSectionsFlat(sanitizedSections).map(s => s.id);
        setExpandedSections(new Set(allIds));

      } catch (error) {
        console.error("Failed to fetch document:", error);
        showNotification(`Failed to load document: ${error instanceof Error ? error.message : String(error)}`, 'error');
        // Optionally, reset to a default empty state or show an error message
        setDocData({
          id: generateId(), title: "Error Loading Document", description: "Could not load document data.",
          categories: [], sourceUrl: "", dateCreated: "", dateModified: new Date().toISOString().split('T')[0],
          author: "", version: "", tags: [], customFields: {}
        });
        setContent("");
        setSections([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [filename]); // Re-run effect when filename changes

  // UI State
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);
  const [showMetadataPanel, setShowMetadataPanel] = useState(true);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set()); // Initialize as empty
  const [isEditingContent, setIsEditingContent] = useState(false);
  const [showJsonPreview, setShowJsonPreview] = useState(false);
  const [notification, setNotification] = useState<Notification | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showColorHighlights, setShowColorHighlights] = useState(true);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const contentDisplayRef = useRef<HTMLDivElement>(null); // Ref for the content display area

  // --- Utility Functions ---
interface Notification {
    message: string;
    type: 'success' | 'error';
}

type ShowNotification = (message: string, type?: 'success' | 'error') => void;

const showNotification: ShowNotification = useCallback((message, type = 'success') => {
    setNotification({ message, type });
    const timer = setTimeout(() => {
        setNotification(null);
    }, 3000);
    return () => clearTimeout(timer);
}, []);

  // Deep clone utility
const deepClone = <T,>(obj: T): T => JSON.parse(JSON.stringify(obj));

  // Find a node by ID (recursive)
interface FindNodeById {
    (nodes: SectionNode[], targetId: string): SectionNode | null;
}

const findNodeById: FindNodeById = useCallback((nodes, targetId) => {
    for (const node of nodes) {
        if (node.id === targetId) return node;
        if (node.children) {
            const found = findNodeById(node.children, targetId);
            if (found) return found;
        }
    }
    return null;
}, []);

  // Get path to node
interface GetNodePath {
    (
        nodes: SectionNode[],
        targetId: string,
        path?: SectionNode[]
    ): SectionNode[] | null;
}

const getNodePath: GetNodePath = useCallback(
    (nodes, targetId, path = []) => {
        for (const node of nodes) {
            if (node.id === targetId) return [...path, node];
            if (node.children) {
                const found = getNodePath(node.children, targetId, [...path, node]);
                if (found) return found;
            }
        }
        return null;
    },
    []
);

  // Update node in tree
interface UpdateNodeInTreeFn {
    (node: SectionNode): SectionNode;
}

interface UpdateNodeInTree {
    (
        nodes: SectionNode[],
        targetId: string,
        updateFn: UpdateNodeInTreeFn
    ): SectionNode[];
}

const updateNodeInTree: UpdateNodeInTree = useCallback(
    (nodes, targetId, updateFn) => {
        return nodes.map((node: SectionNode) => {
            if (node.id === targetId) {
                // Ensure the new node object is created
                const newNode = updateFn(node);
                // If it's the target node, we return the updated one
                return newNode;
            }
            if (node.children) {
                // Recursively update children, but only create new child array if children changed
                const updatedChildren = updateNodeInTree(node.children, targetId, updateFn);
                if (updatedChildren !== node.children) { // Check if children array reference changed
                    return {
                        ...node,
                        children: updatedChildren
                    };
                }
            }
            return node; // Return original node if no changes in it or its children
        });
    },
    []
);

  // Delete node from tree
interface DeleteNodeFromTree {
    (nodes: SectionNode[], targetId: string): SectionNode[];
}

const deleteNodeFromTree: DeleteNodeFromTree = useCallback(
    (nodes, targetId) => {
        return nodes
            .filter((node: SectionNode) => node.id !== targetId)
            .map((node: SectionNode) => ({
                ...node,
                children: node.children ? deleteNodeFromTree(node.children, targetId) : [],
            }));
    },
    []
);

  // Get all sections as flat array
interface GetAllSectionsFlat {
    (nodes: SectionNode[], result?: SectionNode[]): SectionNode[];
}

const getAllSectionsFlat: GetAllSectionsFlat = useCallback(
    (nodes, result = []) => {
        nodes.forEach((node: SectionNode) => {
            result.push(node);
            if (node.children) {
                getAllSectionsFlat(node.children, result);
            }
        });
        return result;
    },
    []
);

  // --- Content Management ---
interface HandleContentChange {
    (newContent: string): void;
}

const handleContentChange: HandleContentChange = useCallback((newContent: string) => {
    setContent(newContent);
    setDocData(prev => ({ ...prev, dateModified: new Date().toISOString().split('T')[0] }));
}, []);

  // Handle text selection for section boundaries
  const handleContentSelection = useCallback(() => {
    if (!selectedSectionId) {
      showNotification("Please select a section first", 'error');
      return;
    }

    let selectionStart: number | undefined;
    let selectionEnd: number | undefined;

    if (isEditingContent && textareaRef.current) {
      // In edit mode, use textarea selection - this path is generally robust
      selectionStart = textareaRef.current.selectionStart;
      selectionEnd = textareaRef.current.selectionEnd;
    } else {
      // In view mode, use window selection
      const selection = window.getSelection();
      const contentDisplayElement = contentDisplayRef.current;

      if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
        showNotification("Please select some text in the content area", 'error');
        return;
      }

      const range = selection.getRangeAt(0);

      // Ensure the selection is within our content display area
      if (!contentDisplayElement || !contentDisplayElement.contains(range.commonAncestorContainer)) {
        showNotification("Please select text within the content area", 'error');
        return;
      }

      // Calculate start and end offsets relative to the *plain text content* of contentDisplayElement
      // This is more robust against HTML structuring (like spans for highlighting)
      const preSelectionRange = document.createRange();
      preSelectionRange.setStart(contentDisplayElement, 0); // Start at the beginning of the content display div
      preSelectionRange.setEnd(range.startContainer, range.startOffset);
      selectionStart = preSelectionRange.toString().length;

      const selectedText = selection.toString();
      selectionEnd = selectionStart + selectedText.length;

      // Final check for empty selection after conversion
      if (selectionStart === selectionEnd) {
        showNotification("Please select some text in the content area", 'error');
        return;
      }
    }

    // Ensure selectionStart and selectionEnd are defined and valid
    if (selectionStart === undefined || selectionEnd === undefined || selectionStart === selectionEnd) {
        showNotification("Failed to determine a valid text selection. Please try again.", 'error');
        return;
    }

    // Update the section with the new positions
    setSections(prev => updateNodeInTree(prev, selectedSectionId, node => ({
      ...node,
      startPosition: selectionStart!,
      endPosition: selectionEnd!
    })));

    showNotification(`Section boundaries updated (${selectionStart} - ${selectionEnd})`);
    
    // Clear the selection
    if (window.getSelection) {
      const selection = window.getSelection();
      if (selection) {
        selection.removeAllRanges();
      }
    }
  }, [selectedSectionId, isEditingContent, updateNodeInTree, showNotification]);

  // Get content preview for a section
interface SectionPreview {
    (section: SectionNode): string;
}

const getSectionPreview: SectionPreview = useCallback((section: SectionNode): string => {
    if (!content || section.startPosition >= section.endPosition) return "";
    const preview = content.substring(section.startPosition, section.endPosition);
    return preview.length > 100 ? preview.substring(0, 100) + "..." : preview;
}, [content]);

  // --- Document Management ---
interface HandleDocumentChange {
    (field: keyof DocumentData, value: string): void;
}

const handleDocumentChange: HandleDocumentChange = useCallback((field, value) => {
    setDocData(prev => ({ 
        ...prev, 
        [field]: value,
        dateModified: new Date().toISOString().split('T')[0]
    }));
}, []);

interface AddDocumentCategory {
    (category: string): void;
}

const addDocumentCategory: AddDocumentCategory = useCallback((category: string) => {
    setDocData(prev => ({
        ...prev,
        categories: [...prev.categories, category]
    }));
    showNotification(`Category "${category}" added`);
}, [showNotification]);

interface RemoveDocumentCategory {
    (category: string): void;
}

const removeDocumentCategory: RemoveDocumentCategory = useCallback((category: string) => {
    setDocData(prev => ({
        ...prev,
        categories: prev.categories.filter((c: string) => c !== category)
    }));
    showNotification(`Category "${category}" removed`);
}, [showNotification]);

interface AddDocumentCustomField {
    (key: string, value: string): void;
}

const addDocumentCustomField: AddDocumentCustomField = useCallback((key, value) => {
    setDocData(prev => ({
        ...prev,
        customFields: { ...prev.customFields, [key]: value }
    }));
    showNotification(`Custom field "${key}" added`);
}, [showNotification]);

interface UpdateDocumentCustomField {
    (oldKey: string, newKey: string, value: string): void;
}

const updateDocumentCustomField: UpdateDocumentCustomField = useCallback((oldKey, newKey, value) => {
    setDocData(prev => {
        const newFields = { ...prev.customFields };
        if (oldKey !== newKey) {
            delete newFields[oldKey];
        }
        newFields[newKey] = value;
        return { ...prev, customFields: newFields };
    });
}, []);

interface DeleteDocumentCustomField {
    (key: string): void;
}

const deleteDocumentCustomField: DeleteDocumentCustomField = useCallback((key: string) => {
    setDocData(prev => {
        const newFields = { ...prev.customFields };
        delete newFields[key];
        return { ...prev, customFields: newFields };
    });
    showNotification(`Custom field "${key}" deleted`);
}, [showNotification]);

  // --- Section Management ---
interface HandleSectionChange {
    (sectionId: string, field: keyof SectionNode, value: any): void;
}

const handleSectionChange: HandleSectionChange = useCallback(
    (sectionId, field, value) => {
        setSections(prev =>
            updateNodeInTree(prev, sectionId, node => ({
                ...node,
                [field]: value,
            }))
        );
    },
    [updateNodeInTree]
);

interface AddSectionCategory {
    (sectionId: string, category: string): void;
}

const addSectionCategory: AddSectionCategory = useCallback(
    (sectionId, category) => {
        setSections(prev =>
            updateNodeInTree(prev, sectionId, node => ({
                ...node,
                categories: [...(node.categories || []), category]
            }))
        );
        showNotification(`Category added`);
    },
    [updateNodeInTree, showNotification]
);

interface RemoveSectionCategory {
    (sectionId: string, category: string): void;
}

const removeSectionCategory: RemoveSectionCategory = useCallback(
    (sectionId, category) => {
        setSections(prev => updateNodeInTree(prev, sectionId, node => ({
            ...node,
            categories: (node.categories || []).filter((c: string) => c !== category)
        })));
        showNotification(`Category removed`);
    },
    [updateNodeInTree, showNotification]
);

interface AddSectionCustomField {
    (sectionId: string, key: string, value: string): void;
}

const addSectionCustomField: AddSectionCustomField = useCallback(
    (sectionId, key, value) => {
        setSections(prev =>
            updateNodeInTree(prev, sectionId, node => ({
                ...node,
                customFields: { ...(node.customFields || {}), [key]: value }
            }))
        );
        showNotification(`Custom field added`);
    },
    [updateNodeInTree, showNotification]
);

interface UpdateSectionCustomField {
    (sectionId: string, oldKey: string, newKey: string, value: string): void;
}

const updateSectionCustomField: UpdateSectionCustomField = useCallback(
    (sectionId, oldKey, newKey, value) => {
        setSections(prev => updateNodeInTree(prev, sectionId, (node: SectionNode) => {
            const newFields: CustomFields = { ...(node.customFields || {}) };
            if (oldKey !== newKey) {
                delete newFields[oldKey];
            }
            newFields[newKey] = value;
            return { ...node, customFields: newFields };
        }));
    },
    [updateNodeInTree]
);

interface DeleteSectionCustomField {
    (sectionId: string, key: string): void;
}

const deleteSectionCustomField: DeleteSectionCustomField = useCallback(
    (sectionId, key) => {
        setSections(prev => updateNodeInTree(prev, sectionId, (node: SectionNode) => {
            const newFields: CustomFields = { ...(node.customFields || {}) };
            delete newFields[key];
            return { ...node, customFields: newFields };
        }));
        showNotification(`Custom field deleted`);
    },
    [updateNodeInTree, showNotification]
);

  const addNewSection = useCallback((parentId: string | null = null) => {
    const newSection = {
      id: generateId(),
      title: parentId ? "New Subsection" : "New Section",
      categories: ["general"],
      startPosition: 0,
      endPosition: 0,
      customFields: {
        importance: "medium",
        lastUpdated: new Date().toISOString().split('T')[0]
      },
      children: []
    };

    if (parentId) {
      setSections(prev => updateNodeInTree(prev, parentId, node => ({
        ...node,
        children: [...(node.children || []), newSection]
      })));
    } else {
      setSections(prev => [...prev, newSection]);
    }

    setExpandedSections(prev => new Set([...prev, newSection.id]));
    showNotification(`${parentId ? 'Subsection' : 'Section'} added`);
  }, [updateNodeInTree, showNotification]);

interface DeleteSectionFn {
    (sectionId: string): void;
}

const deleteSection: DeleteSectionFn = useCallback(
    (sectionId: string) => {
        const section = findNodeById(sections, sectionId);
        if (!section) return;

        // Using a custom modal/dialog instead of window.confirm
        const userConfirmed = window.confirm(`Delete "${section.title}" and all its children?`); // Replace with custom modal later
        if (userConfirmed) {
            setSections((prev: SectionNode[]) => deleteNodeFromTree(prev, sectionId));
            if (selectedSectionId === sectionId) {
                setSelectedSectionId(null);
            }
            showNotification(`Section deleted`, 'error');
        }
    },
    [sections, selectedSectionId, findNodeById, deleteNodeFromTree, showNotification]
);

interface ToggleSectionExpansion {
    (sectionId: string): void;
}

const toggleSectionExpansion: ToggleSectionExpansion = useCallback((sectionId: string) => {
    setExpandedSections((prev: Set<string>) => {
        const newSet = new Set(prev);
        if (newSet.has(sectionId)) {
            newSet.delete(sectionId);
        } else {
            newSet.add(sectionId);
        }
        return newSet;
    });
}, []);

  // --- Search functionality ---
  const filteredSections = useMemo(() => {
    if (!searchQuery) return sections;
    
    const query = searchQuery.toLowerCase();
    interface FilterNode {
      (nodes: SectionNode[]): SectionNode[];
    }

    const filterNodes: FilterNode = (nodes) => {
      // Create a deep copy to ensure immutability for filtering process
      // and to avoid modifying the original 'sections' state when filtering
      const filteredResult: SectionNode[] = [];
      nodes.forEach(node => {
        const matchesSearch =
          node.title.toLowerCase().includes(query) ||
          node.categories?.some((cat: string) => cat.toLowerCase().includes(query)) ||
          Object.values(node.customFields || {}).some((val: string) =>
            val.toString().toLowerCase().includes(query)
          );

        // Recursively filter children
        let filteredChildren: SectionNode[] = [];
        if (node.children && node.children.length > 0) {
          filteredChildren = filterNodes(node.children);
        }

        // If node matches search or any of its children match, include it
        if (matchesSearch || filteredChildren.length > 0) {
          filteredResult.push({
            ...node,
            children: filteredChildren // Assign filtered children
          });
        }
      });
      return filteredResult;
    };
    
    return filterNodes(sections); // Filter the original sections directly
  }, [sections, searchQuery]);

  // --- Color Management ---
  const sectionColors = useMemo(() => {
    const colors = [
      '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', 
      '#EC4899', '#14B8A6', '#F97316', '#6366F1', '#84CC16'
    ];
    const colorMap: { [id: string]: string } = {};
    
    interface SectionColorMap {
        [id: string]: string;
    }

    const assignColors = (
        nodes: SectionNode[],
        depth: number = 0
    ): void => {
        nodes.forEach((node: SectionNode, index: number) => {
            const colorIndex = (depth * 3 + index) % colors.length;
            colorMap[node.id] = colors[colorIndex];
            if (node.children) {
                assignColors(node.children, depth + 1);
            }
        });
    };
    
    assignColors(sections);
    return colorMap;
  }, [sections]);

  // Get highlighted content segments
  const getHighlightedSegments = useMemo(() => {
    // Array to store the final segments for rendering
    const segments: Array<{ text: string; color: string | null; sectionId: string | null; sectionTitle?: string; start: number; end: number }> = [];
    
    // Create a temporary array to hold highlight information for each character position
    // Initialize with no highlight
    const charHighlightInfo = Array(content.length).fill(null).map(() => ({
      sectionId: null as string | null,
      color: null as string | null,
      sectionTitle: undefined as string | undefined
    }));

    // Get all sections as a flat array
    const allSections = getAllSectionsFlat(sections);
    
    // Sort sections for consistent "last one wins" behavior in case of overlaps.
    // Priority: selected section > sections with later start position > default order
    const sortedSectionsForHighlighting = allSections
      .filter(s => s.startPosition < s.endPosition) // Only consider valid sections
      .sort((a, b) => {
        // High priority for the currently selected section, it should "win" any overlap
        if (a.id === selectedSectionId) return 1;
        if (b.id === selectedSectionId) return -1;
        
        // For other sections, sort by start position to ensure consistent overlap resolution.
        // Sections that start later will "paint over" earlier ones if they overlap.
        return a.startPosition - b.startPosition;
      });
    
    // Apply highlights from sections to charHighlightInfo array.
    // This loop effectively "paints" the highlights onto the character array.
    // If sections overlap, the one processed later (due to sort order) will overwrite
    // the highlight information for the overlapping characters.
    sortedSectionsForHighlighting.forEach(section => {
      const sectionColor = sectionColors[section.id];
      for (let i = section.startPosition; i < section.endPosition && i < content.length; i++) {
        charHighlightInfo[i] = {
          sectionId: section.id,
          color: sectionColor,
          sectionTitle: section.title
        };
      }
    });

    // Iterate through charHighlightInfo to consolidate into renderable segments
    if (content.length === 0) {
      return []; // Return empty if no content
    }

    let currentSegmentStart = 0;
    // Get initial highlight properties, handling empty content scenario
    let currentHighlightProps = charHighlightInfo[0] || { sectionId: null, color: null, sectionTitle: undefined };

    // Loop through each character position (including an implicit 'end' position after the last char)
    for (let i = 1; i <= content.length; i++) {
      // Get highlight properties for the next character (or end of content)
      const nextHighlightProps = charHighlightInfo[i] || { sectionId: null, color: null, sectionTitle: undefined };

      // Check if the highlighting properties have changed from the current segment's properties,
      // or if we've reached the end of the content.
      const highlightPropsChanged =
        currentHighlightProps.sectionId !== nextHighlightProps.sectionId ||
        currentHighlightProps.color !== nextHighlightProps.color ||
        currentHighlightProps.sectionTitle !== nextHighlightProps.sectionTitle;

      if (highlightPropsChanged || i === content.length) {
        // If properties changed or end of content, the current segment ends here.
        // Add the completed segment to our list.
        segments.push({
          text: content.substring(currentSegmentStart, i),
          color: currentHighlightProps.color,
          sectionId: currentHighlightProps.sectionId,
          sectionTitle: currentHighlightProps.sectionTitle,
          start: currentSegmentStart,
          end: i
        });
        // Start a new segment from the current position with the new properties.
        currentSegmentStart = i;
        currentHighlightProps = nextHighlightProps;
      }
    }
    
    return segments;
  }, [content, sections, sectionColors, getAllSectionsFlat, selectedSectionId]); // Added selectedSectionId to dependencies

  // --- Export/Import ---
  const exportDocument = useCallback(() => {
    // Create a deep copy of sections to add highlightedContent without modifying original state
    const sectionsWithHighlightedContent: SectionNode[] = deepClone(sections).map((section: SectionNode) => {
      const newSection = { ...section };
      if (newSection.startPosition < newSection.endPosition && content) {
        newSection.highlightedContent = content.substring(newSection.startPosition, newSection.endPosition);
      } else {
        newSection.highlightedContent = ""; // Ensure it's always present or explicitly empty
      }
      // Recursively process children
      if (newSection.children && newSection.children.length > 0) {
        const processChildren = (nodes: SectionNode[]): SectionNode[] => {
            return nodes.map((childNode: SectionNode) => {
                const newChildNode = { ...childNode };
                if (newChildNode.startPosition < newChildNode.endPosition && content) {
                    newChildNode.highlightedContent = content.substring(newChildNode.startPosition, newChildNode.endPosition);
                } else {
                    newChildNode.highlightedContent = "";
                }
                if (newChildNode.children && newChildNode.children.length > 0) {
                    newChildNode.children = processChildren(newChildNode.children);
                }
                return newChildNode;
            });
        };
        newSection.children = processChildren(newSection.children);
      }
      return newSection;
    });

    const exportData = {
      document: docData,
      content,
      sections: sectionsWithHighlightedContent, // Use the modified sections array
      metadata: {
        exportDate: new Date().toISOString(),
        version: docData.version || "1.0",
        totalSections: getAllSectionsFlat(sections).length // This still uses original sections for count
      }
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${docData.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = window.document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    showNotification('Document exported successfully');
  }, [docData, content, sections, getAllSectionsFlat, showNotification]);

interface ImportDocumentEvent extends React.ChangeEvent<HTMLInputElement> {}

interface ImportData {
    document: DocumentData;
    content?: string;
    sections: SectionNode[];
}

const importDocument = useCallback((event: ImportDocumentEvent) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e: ProgressEvent<FileReader>) => {
        try {
            const importData = JSON.parse(e.target?.result as string) as ImportData;
            
            if (!importData.document || !importData.sections) {
                throw new Error('Invalid document format');
            }

            setDocData(importData.document);
            setContent(importData.content || '');
            
            // Remove 'highlightedContent' if present in imported sections to match SectionNode interface
            const sanitizedSections = importData.sections.map((section: SectionNode) => {
                const newSection = { ...section };
                delete newSection.highlightedContent;
                if (newSection.children && newSection.children.length > 0) {
                    const sanitizeChildren = (nodes: SectionNode[]): SectionNode[] => {
                        return nodes.map((childNode: SectionNode) => {
                            const newChildNode = { ...childNode };
                            delete newChildNode.highlightedContent;
                            if (newChildNode.children && newChildNode.children.length > 0) {
                                newChildNode.children = sanitizeChildren(newChildNode.children);
                            }
                            return newChildNode;
                        });
                    };
                    newSection.children = sanitizeChildren(newSection.children);
                }
                return newSection;
            });
            setSections(sanitizedSections);
            
            // Expand all imported sections
            const allIds = getAllSectionsFlat(importData.sections).map(s => s.id);
            setExpandedSections(new Set(allIds));
            
            showNotification('Document imported successfully');
        } catch (error: any) {
            showNotification('Failed to import document: ' + error.message, 'error');
        }
    };
    reader.readAsText(file);
}, [getAllSectionsFlat, showNotification]);

  // --- Save (Approve) functionality ---
const handleApproveAndSend = useCallback(async () => {
  // Build the export data (same as exportDocument)
  const sectionsWithHighlightedContent: SectionNode[] = deepClone(sections).map((section: SectionNode) => {
    const newSection = { ...section };
    if (newSection.startPosition < newSection.endPosition && content) {
      newSection.highlightedContent = content.substring(newSection.startPosition, newSection.endPosition);
    } else {
      newSection.highlightedContent = "";
    }
    if (newSection.children && newSection.children.length > 0) {
      const processChildren = (nodes: SectionNode[]): SectionNode[] => {
        return nodes.map((childNode: SectionNode) => {
          const newChildNode = { ...childNode };
          if (newChildNode.startPosition < newChildNode.endPosition && content) {
            newChildNode.highlightedContent = content.substring(newChildNode.startPosition, newChildNode.endPosition);
          } else {
            newChildNode.highlightedContent = "";
          }
          if (newChildNode.children && newChildNode.children.length > 0) {
            newChildNode.children = processChildren(newChildNode.children);
          }
          return newChildNode;
        });
      };
      newSection.children = processChildren(newSection.children);
    }
    return newSection;
  });

  const exportData = {
    document: docData,
    content,
    sections: sectionsWithHighlightedContent,
    metadata: {
      exportDate: new Date().toISOString(),
      version: docData.version || "1.0",
      totalSections: getAllSectionsFlat(sections).length
    }
  };

  // Use filename prop or fallback to docData.title
  const exportFileName = (filename || docData.title || "document").replace(/[^a-z0-9]/gi, '_').toLowerCase() + ".json";

  try {
    const response = await fetch("http://localhost:8000/upload", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Filename": exportFileName
      },
      body: JSON.stringify(exportData)
    });
    if (!response.ok) {
      throw new Error(`Server responded with status ${response.status}`);
    }
    showNotification('Document approved and sent!', 'success');
  } catch (error: any) {
    showNotification('Failed to send document: ' + error.message, 'error');
  }
}, [docData, content, sections, getAllSectionsFlat, showNotification, filename]);

  // --- Cancel functionality ---
  const handleCancel = useCallback(() => {
    // In a real application, this would typically close the modal or discard changes.
    console.log("Operation cancelled.");
    showNotification('Operation cancelled', 'error');
    // onClose(); // If this component is used in a modal
  }, [showNotification]);


  // Section Item Component (recursive)
  type SectionItemProps = {
    node: SectionNode;
    depth?: number;
    // Pass relevant callbacks as props to avoid re-creating them inside memoized component
    isSelected: boolean;
    isExpanded: boolean;
    toggleSectionExpansion: (id: string) => void;
    addNewSection: (parentId: string | null) => void;
    deleteSection: (id: string) => void;
    setSelectedSectionId: (id: string | null) => void;
    getSectionPreview: (section: SectionNode) => string;
    sectionColors: { [id: string]: string };
    showColorHighlights: boolean;
    handleSectionChange: (sectionId: string, field: keyof SectionNode, value: any) => void;
    handleContentSelection: () => void;
    addSectionCategory: (sectionId: string, category: string) => void;
    removeSectionCategory: (sectionId: string, category: string) => void;
    addSectionCustomField: (sectionId: string, key: string, value: string) => void;
    updateSectionCustomField: (sectionId: string, oldKey: string, newKey: string, value: string) => void;
    deleteSectionCustomField: (sectionId: string, key: string) => void;
    isEditingContent: boolean; // Pass this down for the "Use Selected Text" button info
  };

  const SectionItem: React.FC<SectionItemProps> = memo(({ 
    node, 
    depth = 0,
    isSelected,
    isExpanded,
    toggleSectionExpansion,
    addNewSection,
    deleteSection,
    setSelectedSectionId,
    getSectionPreview,
    sectionColors,
    showColorHighlights,
    handleSectionChange,
    handleContentSelection,
    addSectionCategory,
    removeSectionCategory,
    addSectionCustomField,
    updateSectionCustomField,
    deleteSectionCustomField,
    isEditingContent
  }) => {
    const hasChildren = node.children && node.children.length > 0;
    const preview = getSectionPreview(node);
    const sectionColor = sectionColors[node.id];

    // Local state for input fields to prevent re-renders on every keystroke
    const [editingTitle, setEditingTitle] = useState(node.title);
    const [editingStartPosition, setEditingStartPosition] = useState(node.startPosition.toString());
    const [editingEndPosition, setEditingEndPosition] = useState(node.endPosition.toString());

    // Sync local state with prop changes (e.g., when node prop updates from outside)
    useEffect(() => {
      setEditingTitle(node.title);
    }, [node.title]);

    useEffect(() => {
      setEditingStartPosition(node.startPosition.toString());
    }, [node.startPosition]);

    useEffect(() => {
      setEditingEndPosition(node.endPosition.toString());
    }, [node.endPosition]);

    // Local change handlers
    const handleLocalTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setEditingTitle(e.target.value);
    };

    const handleLocalStartPositionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setEditingStartPosition(e.target.value);
    };

    const handleLocalEndPositionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setEditingEndPosition(e.target.value);
    };

    // Blur handlers to update global state
    const handleTitleBlur = () => {
      if (editingTitle !== node.title) {
        handleSectionChange(node.id, 'title', editingTitle);
      }
    };

    const handleStartPositionBlur = () => {
      const newPos = parseInt(editingStartPosition) || 0;
      if (newPos !== node.startPosition) {
        handleSectionChange(node.id, 'startPosition', newPos);
      }
    };

    const handleEndPositionBlur = () => {
      const newPos = parseInt(editingEndPosition) || 0;
      if (newPos !== node.endPosition) {
        handleSectionChange(node.id, 'endPosition', newPos);
      }
    };

    // KeyPress handler for 'Enter' to trigger blur (and thus save)
    const handleInputKeyPress = (e: React.KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      if (e.key === 'Enter') {
        e.currentTarget.blur(); // Trigger blur to save the changes
      }
    };

    return (
      <div className={`${depth > 0 ? 'ml-4' : ''}`}>
        <div
          className={`border rounded-lg mb-2 ${
            isSelected ? 'border-[#3C04FC] shadow-md' : 'border-gray-200'
          }`}
        >
          <div
            className={`p-3 cursor-pointer transition-colors ${
              isSelected ? 'bg-gradient-to-r from-[#3C04FC]/5 to-[#BB4CD8]/5' : 'hover:bg-gray-50'
            }`}
            onClick={() => setSelectedSectionId(isSelected ? null : node.id)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 flex-1">
                {hasChildren && ( // Only show expand/collapse if section has children
                  <IconButton
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleSectionExpansion(node.id);
                    }}
                    tooltip={isExpanded ? "Collapse" : "Expand"}
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                    )}
                  </IconButton>
                )}
                
                {/* Color indicator */}
                {showColorHighlights && node.startPosition < node.endPosition && (
                  <div 
                    className="w-2 h-8 rounded"
                    style={{ backgroundColor: sectionColor }}
                    title="Section color in content"
                  />
                )}
                
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900">{node.title}</h4>
                  {preview && (
<p className="text-xs text-gray-500 mt-1 line-clamp-2">{preview}</p>
                  )}
                  <div className="flex items-center gap-2 mt-1">
                    {node.categories?.slice(0, 3).map((cat, i) => (
                      <span key={i} className="text-xs px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">
                        {cat}
                      </span>
                    ))}
                    {node.categories?.length > 3 && (
                      <span className="text-xs text-gray-500">+{node.categories.length - 3}</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-1">
                {hasChildren && (
                  <span className="text-xs text-gray-500 mr-2">{node.children.length}</span>
                )}
                <IconButton
                  onClick={(e) => {
                    e.stopPropagation();
                    addNewSection(node.id);
                  }}
                  tooltip="Add subsection"
                >
                  <Plus className="w-4 h-4 text-gray-600" />
                </IconButton>
                <IconButton
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSection(node.id);
                  }}
                  tooltip="Delete section"
                  className="hover:text-red-600"
                >
                  <Trash2 className="w-4 h-4" />
                </IconButton>
              </div>
            </div>
          </div>

          {isSelected && ( 
            <div className="border-t border-gray-200 bg-gray-50 p-4 space-y-3">
              <LabeledInput
                inputKey={`${node.id}-title`}
                label="Title"
                value={editingTitle}
                onChange={handleLocalTitleChange}
                onBlur={handleTitleBlur} // Add onBlur handler
                onKeyPress={handleInputKeyPress} // Add onKeyPress handler
                placeholder="Section title"
              />
              
              <div className="grid grid-cols-2 gap-3">
                <LabeledInput
                  inputKey={`${node.id}-startPosition`}
                  label="Start Position"
                  type="number"
                  value={editingStartPosition}
                  onChange={handleLocalStartPositionChange}
                  onBlur={handleStartPositionBlur} // Add onBlur handler
                  onKeyPress={handleInputKeyPress} // Add onKeyPress handler
                  placeholder="0"
                />
                <LabeledInput
                  inputKey={`${node.id}-endPosition`}
                  label="End Position"
                  type="number"
                  value={editingEndPosition}
                  onChange={handleLocalEndPositionChange}
                  onBlur={handleEndPositionBlur} // Add onBlur handler
                  onKeyPress={handleInputKeyPress} // Add onKeyPress handler
                  placeholder="0"
                />
              </div>

              <div className="text-xs text-gray-500 text-center">
                {node.startPosition < node.endPosition ? (
                  <span>Currently showing characters {node.startPosition} to {node.endPosition}</span>
                ) : (
                  <span>No content range defined</span>
                )}
              </div>

              <button
                onClick={handleContentSelection}
                className="w-full py-2 px-3 bg-[#3C04FC] text-white text-sm rounded-lg hover:bg-[#3C04FC]/90 transition-colors flex items-center justify-center group"
                title="Select text in the content area, then click this button"
              >
                <Copy className="w-4 h-4 mr-2" />
                Use Selected Text
                <span className="ml-2 text-xs opacity-75 group-hover:opacity-100">
                  {isEditingContent ? '(Edit mode)' : '(View mode)'}
                </span>
              </button>
              
              <p className="text-xs text-gray-400 text-center mt-1">
                Works in both edit and view modes
              </p>

              <CategoryManager
                categories={node.categories}
                onAdd={(cat) => addSectionCategory(node.id, cat)}
                onRemove={(cat) => removeSectionCategory(node.id, cat)}
              />

              <CustomFieldManager
                customFields={node.customFields}
                onAdd={(key, value) => addSectionCustomField(node.id, key, value)}
                onUpdate={(oldKey, newKey, value) => updateSectionCustomField(node.id, oldKey, newKey, value)}
                onDelete={(key) => deleteSectionCustomField(node.id, key)}
              />
            </div>
          )}
        </div>

        {isExpanded && hasChildren && ( // Children are still only shown if expanded and hasChildren
          <div className="ml-2">
            {node.children.map(child => (
              <SectionItem 
                key={child.id} // Ensure key is on the mapped component
                node={child} 
                depth={depth + 1}
                isSelected={selectedSectionId === child.id}
                isExpanded={expandedSections.has(child.id)}
                toggleSectionExpansion={toggleSectionExpansion}
                addNewSection={addNewSection}
                deleteSection={deleteSection}
                setSelectedSectionId={setSelectedSectionId}
                getSectionPreview={getSectionPreview}
                sectionColors={sectionColors}
                showColorHighlights={showColorHighlights}
                handleSectionChange={handleSectionChange}
                handleContentSelection={handleContentSelection}
                addSectionCategory={addSectionCategory}
                removeSectionCategory={removeSectionCategory}
                addSectionCustomField={addSectionCustomField}
                updateSectionCustomField={updateSectionCustomField}
                deleteSectionCustomField={deleteSectionCustomField}
                isEditingContent={isEditingContent}
              />
            ))}
          </div>
        )}
      </div>
    );
  });

  SectionItem.displayName = 'SectionItem'; // For easier debugging with React DevTools

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg flex items-center space-x-2 z-50 transition-all ${
          notification.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        }`}>
          {notification.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span>{notification.message}</span>
        </div>
      )}

      {/* Sidebar */}
      <div className={`${showMetadataPanel ? 'w-96' : 'w-16'} bg-white border-r border-gray-200 transition-all duration-300 flex flex-col shadow-lg`}>
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          {showMetadataPanel && (
            <h2 className="font-semibold text-gray-900 text-lg flex items-center">
              <FolderTree className="w-5 h-5 mr-2 text-[#3C04FC]" />
              Document Structure
            </h2>
          )}
          <IconButton
            onClick={() => setShowMetadataPanel(!showMetadataPanel)}
            tooltip={showMetadataPanel ? "Hide panel" : "Show panel"}
          >
            {showMetadataPanel ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </IconButton>
        </div>

        {showMetadataPanel && (
          <div className="flex-1 overflow-y-auto">
            {/* Search */}
            <div className="p-4 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search sections..."
                  className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3C04FC] focus:border-transparent"
                />
              </div>
            </div>

            {/* Document Metadata */}
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                <FileText className="w-4 h-4 mr-2 text-[#3C04FC]" />
                Document Info
              </h3>
              <div className="space-y-3">
                <LabeledInput
                  label="Title"
                  value={docData.title}
                  onChange={(e) => handleDocumentChange('title', e.target.value)}
                  inputKey="doc-title" // Add key for stability
                />
                <LabeledInput
                  label="Description"
                  type="textarea"
                  value={docData.description}
                  onChange={(e) => handleDocumentChange('description', e.target.value)}
                  inputKey="doc-description" // Add key for stability
                />
                <div className="grid grid-cols-2 gap-3">
                  <LabeledInput
                    label="Author"
                    value={docData.author}
                    onChange={(e) => handleDocumentChange('author', e.target.value)}
                    inputKey="doc-author" // Add key for stability
                  />
                  <LabeledInput
                    label="Version"
                    value={docData.version}
                    onChange={(e) => handleDocumentChange('version', e.target.value)}
                    inputKey="doc-version" // Add key for stability
                  />
                </div>
                <CategoryManager
                  categories={docData.categories}
                  onAdd={addDocumentCategory}
                  onRemove={removeDocumentCategory}
                />
                <CustomFieldManager
                  customFields={docData.customFields}
                  onAdd={addDocumentCustomField}
                  onUpdate={updateDocumentCustomField}
                  onDelete={deleteDocumentCustomField}
                />
              </div>
            </div>

            {/* Sections */}
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-gray-900 flex items-center">
                  <Hash className="w-4 h-4 mr-2 text-[#BB4CD8]" />
                  Sections ({getAllSectionsFlat(filteredSections).length})
                </h3>
                <IconButton onClick={() => addNewSection()} tooltip="Add new section">
                  <Plus className="w-4 h-4 text-[#3C04FC]" />
                </IconButton>
              </div>

              <div className="space-y-2">
                {filteredSections.map(section => (
                  <SectionItem 
                    key={section.id} 
                    node={section} 
                    isSelected={selectedSectionId === section.id}
                    isExpanded={expandedSections.has(section.id)}
                    toggleSectionExpansion={toggleSectionExpansion}
                    addNewSection={addNewSection}
                    deleteSection={deleteSection}
                    setSelectedSectionId={setSelectedSectionId}
                    getSectionPreview={getSectionPreview}
                    sectionColors={sectionColors}
                    showColorHighlights={showColorHighlights}
                    handleSectionChange={handleSectionChange}
                    handleContentSelection={handleContentSelection}
                    addSectionCategory={addSectionCategory}
                    removeSectionCategory={removeSectionCategory}
                    addSectionCustomField={addSectionCustomField}
                    updateSectionCustomField={updateSectionCustomField}
                    deleteSectionCustomField={deleteSectionCustomField}
                    isEditingContent={isEditingContent}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4 flex-shrink-0 relative z-10">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-gray-900 flex items-center">
              <LayoutPanelLeft className="w-5 h-5 mr-2 text-[#3C04FC]" />
              {docData.title || "Loading Document..."}
            </h1>
            <div className="flex items-center space-x-2">
              <IconButton
                onClick={() => setIsEditingContent(!isEditingContent)}
                className={isEditingContent ? "bg-[#3C04FC] text-white hover:bg-[#3C04FC]/90" : ""}
                tooltip={isEditingContent ? "View mode" : "Edit mode"}
                disabled={isLoading} // Disable buttons while loading
              >
                {isEditingContent ? <Eye className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
              </IconButton>
              <IconButton
                onClick={() => setShowColorHighlights(!showColorHighlights)}
                className={showColorHighlights ? "text-[#3C04FC]" : ""}
                tooltip={showColorHighlights ? "Hide color highlights" : "Show color highlights"}
                disabled={isLoading} // Disable buttons while loading
              >
                <Type className="w-4 h-4" />
              </IconButton>
              <IconButton onClick={exportDocument} tooltip="Export document" disabled={isLoading}>
                <DownloadCloud className="w-4 h-4" />
              </IconButton>
              <input
                type="file"
                id="importFile"
                accept=".json"
                onChange={importDocument}
                className="hidden"
                disabled={isLoading} // Disable input while loading
              />
              <IconButton 
                onClick={() => {
                  const input = document.getElementById('importFile');
                  if (input) input.click();
                }}
                tooltip="Import document"
                disabled={isLoading} // Disable buttons while loading
              >
                <UploadCloud className="w-4 h-4" />
              </IconButton>
              <IconButton
                onClick={() => setShowJsonPreview(!showJsonPreview)}
                tooltip="Toggle JSON preview"
                disabled={isLoading} // Disable buttons while loading
              >
                <Code className="w-4 h-4" />
              </IconButton>
            </div>
          </div>
          
          <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
            <span className="flex items-center">
              <User className="w-4 h-4 mr-1" />
              {docData.author || "N/A"}
            </span>
            <span className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              Modified: {docData.dateModified || "N/A"}
            </span>
            <span className="flex items-center">
              <Tag className="w-4 h-4 mr-1" />
              v{docData.version || "N/A"}
            </span>
          </div>
        </div>

        {/* JSON Preview */}
        {showJsonPreview && (
          <div className="bg-gray-900 text-green-400 p-4 overflow-auto flex-shrink-0" style={{ maxHeight: '300px' }}>
            <pre className="text-xs whitespace-pre-wrap break-all">
              {JSON.stringify({ document: docData, content, sections }, null, 2)}
            </pre>
          </div>
        )}

        {/* Content Editor */}
        <div className="flex-1 p-6 flex flex-col">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center flex-1 text-gray-500">
              <Loader2 className="w-10 h-10 animate-spin text-[#3C04FC]" />
              <p className="mt-4 text-lg">Loading document...</p>
            </div>
          ) : (
            <>
              {/* Selection Guide */}
              {selectedSectionId && (
                <div className="mb-2 p-2 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                  Select text below and click "Use Selected Text" to define boundaries for: 
                  <span className="font-semibold ml-1">{findNodeById(sections, selectedSectionId)?.title}</span>
                </div>
              )}
              
              {isEditingContent ? (
                <textarea
                  ref={textareaRef}
                  value={content}
                  onChange={(e) => handleContentChange(e.target.value)}
                  className="flex-1 p-4 border border-[#3C04FC] bg-white rounded-lg text-sm leading-relaxed resize-none font-mono focus:ring-2 focus:ring-[#3C04FC]"
                  placeholder="Start typing your document content..."
                />
              ) : (
                <div className="relative flex-1" ref={contentDisplayRef}>
                  <div 
                    id="content-display"
                    className="w-full h-full p-4 border border-gray-300 bg-white rounded-lg text-sm leading-relaxed font-mono overflow-auto"
                    style={{ whiteSpace: 'pre-wrap', userSelect: 'text' }}
                  >
                    {showColorHighlights ? (
                      getHighlightedSegments.map((segment, index) => (
                        <span
                          // Use a stable key based on segment's start, end, and sectionId
                          // This helps React optimize updates and reduces visual flicker
                          key={`${segment.start}-${segment.end}-${segment.sectionId || 'unhighlighted'}`}
                          style={{
                            backgroundColor: segment.color ? `${segment.color}20` : 'transparent',
                            color: segment.color ? segment.color : 'inherit',
                            borderBottom: segment.color ? `2px solid ${segment.color}` : 'none',
                            position: 'relative'
                          }}
                          title={segment.sectionTitle}
                          className={segment.sectionId === selectedSectionId ? 'ring-2 ring-offset-1 ring-[#3C04FC]' : ''}
                        >
                          {segment.text}
                        </span>
                      ))
                    ) : (
                      <span>{content}</span>
                    )}
                    {content.length === 0 && (
                      <span className="text-gray-400">Start typing your document content...</span>
                    )}
                  </div>
                  
                  {/* Draggable Color Legend */}
                  {showColorHighlights && (
                    <DraggableColorLegend 
                      sections={sections}
                      sectionColors={sectionColors}
                      setSelectedSectionId={setSelectedSectionId}
                      getAllSectionsFlat={getAllSectionsFlat}
                      parentRef={contentDisplayRef}
                    />
                  )}
                </div>
              )}
            </>
          )}
        </div>
        
        {/* Footer for Action Buttons */}
        <div className="bg-white border-t border-gray-200 p-4 flex justify-end space-x-2 flex-shrink-0 relative z-10">
          <button
            onClick={handleCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 transition-colors"
            disabled={isLoading} // Disable buttons while loading
          >
            Cancel
          </button>
          <button
            onClick={handleApproveAndSend}
            className="px-4 py-2 text-sm font-medium bg-[#3C04FC] text-white rounded-lg hover:bg-[#3C04FC]/90 transition-colors flex items-center"
            disabled={isLoading} // Disable buttons while loading
          >
            <CheckCircle2 className="w-4 h-4 mr-2" />
            Approve & Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentEditor;
