import {
  Upload,
  Bot,
  Search,
  FileText,
  Zap,
  MessageSquare,
  Database,
  BarChart3,
  Globe,
  Home,
} from "lucide-react";
import React from "react";

// Define the type for navigation items
export interface NavItem {
  name: string;
  label: string;
  icon: () => React.ReactNode;
  href: string;
}

// Sidebar navigation items
export const navItems: NavItem[] = [
  {
    name: "home",
    label: "Home",
    icon: () => <Home className="w-5 h-5" />,
    href: "/",
  },
  {
    name: "search",
    label: "Smart Search",
    icon: () => <Search className="w-5 h-5" />,
    href: "/search-engine",
  },
  {
    name: "chat",
    label: "AI Chat Assistant",
    icon: () => <Bot className="w-5 h-5" />,
    href: "/chatbot",
  },
  {
    name: "scraper",
    label: "Web Scraper",
    icon: () => <Globe className="w-5 h-5" />,
    href: "/scraper",
  },
  {
    name: "database",
    label: "Knowledge Base",
    icon: () => <Database className="w-5 h-5" />,
    href: "/knowledge-base",
  },
  {
    name: "analytics",
    label: "Analytics",
    icon: () => <BarChart3 className="w-5 h-5" />,
    href: "/analytics",
  },
  {
    name: "document-viewer",
    label: "Document Viewer",
    icon: () => <FileText className="w-5 h-5" />,
    href: "/document-viewer",
  },
];

// Type for feature items
export interface FeatureItem {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradientClass: string;
  action: (section: string) => void;
  sectionName: string;
  route: string;
}

// Feature items
export const featureItemsData = (
  setActiveSection: (section: string) => void
): FeatureItem[] => [
  {
    icon: <Upload className="w-8 h-8" />,
    title: "Smart Document Upload",
    description:
      "Drag and drop PDFs, Word docs, spreadsheets, and more. Our AI automatically processes and categorizes your content.",
    gradientClass: "bg-gradient-to-r from-primary to-secondary",
    action: setActiveSection,
    sectionName: "upload",
    route: "/search-engine?view=upload",
  },
  {
    icon: <Search className="w-8 h-8" />,
    title: "OpenSearch Integration",
    description:
      "Lightning-fast search across your entire document library with contextual understanding and semantic matching.",
    gradientClass: "bg-gradient-to-r from-primary to-secondary",
    action: setActiveSection,
    sectionName: "search",
    route: "/smart-search"
  },
  {
    icon: <Bot className="w-8 h-8" />,
    title: "AI Chat Assistant",
    description:
      "Chat with your documents using our RAG-powered bot that provides accurate, context-aware answers.",
    gradientClass: "bg-gradient-to-r from-primary to-secondary",
    action: setActiveSection,
    sectionName: "chat",
    route: "/chatbot"
  },
  {
    icon: <Globe className="w-8 h-8" />,
    title: "Web Scraper",
    description:
      "Don't have documents? Our advanced scraper can extract data from your websites automatically.",
    gradientClass: "bg-gradient-to-r from-primary to-secondary",
    action: setActiveSection,
    sectionName: "scraper",
    route: "/scraper"
  },
  {
    icon: <Database className="w-8 h-8" />,
    title: "Knowledge Base",
    description:
      "Organize and manage your processed documents in a structured, searchable knowledge repository.",
    gradientClass: "bg-gradient-to-r from-primary to-secondary",
    action: setActiveSection,
    sectionName: "database",
    route: "/knowledge-base"
  },
  {
    icon: <BarChart3 className="w-8 h-8" />,
    title: "Analytics Dashboard",
    description:
      "Track usage patterns, popular queries, and document performance with detailed analytics.",
    gradientClass: "bg-gradient-to-r from-primary to-secondary",
    action: setActiveSection,
    sectionName: "analytics",
    route: "/analytics"
  },
];

// Quick start steps
export interface QuickStartStepItem {
  stepNumber: string;
  icon: React.ReactNode;
  title: string;
  description: string;
}

export const quickStartStepsData: QuickStartStepItem[] = [
  {
    stepNumber: "1",
    icon: <FileText className="w-10 h-10" />,
    title: "Upload or Scrape",
    description:
      "Add your documents or let our scraper collect data from your websites",
  },
  {
    stepNumber: "2",
    icon: <Zap className="w-10 h-10" />,
    title: "AI Processing",
    description:
      "Our RAG technology processes and indexes your content with OpenSearch",
  },
  {
    stepNumber: "3",
    icon: <MessageSquare className="w-10 h-10" />,
    title: "Ask Questions",
    description:
      "Chat with your documents and get intelligent, contextual answers",
  },
];

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  documentsCount: number;
  scrapedPagesCount: number;
  category?: string;
}

// These are the knowledge bases that were added in the previous turn's DocumentViewer component for demonstration.
export const knowledgeBases: KnowledgeBase[] = [
  {
    id: "kb-1",
    name: "HR Policies",
    description: "Company's official human resources policies and procedures.",
    documentsCount: 120,
    scrapedPagesCount: 500,
  },
  {
    id: "kb-2",
    name: "IT Support Docs",
    description: "Technical guides and solutions for IT-related issues.",
    documentsCount: 85,
    scrapedPagesCount: 300,
  },
  {
    id: "kb-3",
    name: "Legal Compliance",
    description: "Documents related to legal and regulatory compliance.",
    documentsCount: 45,
    scrapedPagesCount: 150,
  },
];

export interface ChatMessage {
  type: "user" | "bot";
  text: string;
}

export const initialSuggestions: string[] = [
  "How do Higher Loss Absorbency (HLA) capital requirements impact systemically important banks?",
  "What are the key criteria for obtaining a banking license under the CBB's Licensing Requirements Module?",
  "What fundamental obligations must all CBB conventional bank licensees adhere to under the Principles of Business?",
];

export const mockChatHistory: string[] = [
  "CSB Selected Volume Overview",
  "CIU Obligations and Liability Limitati",
  "Insurance Code Principles",
  "Discussing CBB",
  "GCC Fund Passporting Regime Expla",
  "Bank Communication Standards Dis",
  "Islamic Bank Licensees Auditor Rec",
  "Discussing Insurance License Requ",
  "Conventional Banking Business Prin",
  "Brief and Casual Chat",
  "CBB Banking Regulatory Compli",
  "Bahrain Banking Regulatory Compli",
  "Addressing Customer Information N",
  "Discussing Unwritten Rules and Loc",
];

interface CustomFields {
  [key: string]: string;
}

interface SectionNode {
  id: string;
  title: string;
  categories: string[];
  startPosition: number;
  endPosition: number;
  customFields: CustomFields;
  children: SectionNode[];
  highlightedContent?: string;
}

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

interface FullDocumentExport {
  document: DocumentData;
  content: string;
  sections: SectionNode[];
  metadata?: {
    exportDate: string;
    version: string;
    totalSections: number;
  };
}

export const MOCK_DOCUMENT_JSON: FullDocumentExport = {
  document: {
    id: "random-doc-id-123",
    title: "Employment Law Guidelines 2024",
    description:
      "Comprehensive employment law guidelines covering worker rights, employer obligations, and compliance requirements.",
    categories: ["legal", "employment", "compliance", "2024"],
    sourceUrl: "https://legal.gov/employment-law-2024",
    dateCreated: "2024-01-15",
    dateModified: "2024-06-24",
    author: "Legal Department",
    version: "1.0",
    tags: ["employment", "legal", "compliance", "2024"],
    customFields: {
      jurisdiction: "Federal",
      effectiveDate: "2024-01-01",
      reviewCycle: "Annual",
      confidentiality: "Public",
    },
  },
  content: `EMPLOYMENT LAW GUIDELINES 2024

SECTION 1: WORKER RIGHTS AND PROTECTIONS

1.1 Fundamental Rights
Every worker has the right to fair wages, safe working conditions, and protection from discrimination. These rights are guaranteed under federal and state employment laws.

1.1.1 Minimum Wage and Overtime
Workers are entitled to minimum wage compensation as defined by current legislation and overtime pay for hours worked beyond the standard work week.

1.1.2 Workplace Safety and Health
Employers must provide a safe and healthy workplace environment, free from recognized hazards.

1.1.3 Protection from Discrimination and Harassment
Workers are protected from harassment and discrimination based on protected characteristics, as per federal statutes.

SECTION 2: EMPLOYER OBLIGATIONS AND COMPLIANCE

2.1 Compliance Requirements
Employers must maintain compliance with all applicable employment laws and regulations. This includes proper classification of workers, adherence to wage and hour laws, and implementation of anti-discrimination policies.

2.1.1 Worker Classification
Proper classification of employees vs. independent contractors is crucial for tax and labor law compliance.

2.1.2 Record Keeping
Accurate record-keeping for wages, hours, and employment terms is mandated by law.

2.2 Safety Standards
Workplace safety is a fundamental obligation. Employers must provide a workplace free from recognized hazards and comply with OSHA standards.

2.2.1 OSHA Compliance
Compliance with Occupational Safety and Health Administration (OSHA) standards is mandatory for most workplaces.

2.2.2 Hazard Communication
Employers are required to inform employees about potential chemical hazards in the workplace.

SECTION 3: EMPLOYMENT TERMINATION

3.1 At-Will Employment
Most employment in the U.S. is at-will, meaning either party can terminate the relationship at any time, with or without cause, unless a contract or law specifies otherwise.

3.2 Wrongful Termination
Exceptions to at-will employment include termination based on discrimination, retaliation, or breach of contract.

SECTION 4: LEAVE POLICIES

4.1 Family and Medical Leave Act (FMLA)
Eligible employees are entitled to unpaid, job-protected leave for specific family and medical reasons.

4.2 Paid Sick Leave
Many states and localities require employers to provide paid sick leave to employees.
`,
  sections: [
    {
      id: "section-worker-rights",
      title: "Worker Rights and Protections",
      categories: ["worker-rights", "protections", "fundamental"],
      startPosition: 32,
      endPosition: 778,
      customFields: {
        importance: "critical",
        lastUpdated: "2024-01-15",
        sourceReference: "https://www.cbb.gov.bh/rulebook/volume-1/module-hr",
        legalBasis: "Federal Labor Standards",
      },
      children: [
        {
          id: "subsection-fundamental-rights",
          title: "Fundamental Rights",
          categories: ["fundamental", "basic-rights"],
          startPosition: 77,
          endPosition: 778,
          customFields: {
            constitutionalBasis: "14th Amendment",
            scope: "All employees",
          },
          children: [
            {
              id: "subsection-min-wage-overtime",
              title: "Minimum Wage and Overtime",
              categories: ["wage", "FLSA", "overtime"],
              startPosition: 265,
              endPosition: 410,
              customFields: {
                act: "FLSA",
                enforcement: "Department of Labor",
              },
              children: [],
            },
            {
              id: "subsection-workplace-safety",
              title: "Workplace Safety and Health",
              categories: ["safety", "health"],
              startPosition: 412,
              endPosition: 521,
              customFields: {
                regulator: "OSHA",
              },
              children: [],
            },
            {
              id: "subsection-discrimination-harassment",
              title: "Protection from Discrimination and Harassment",
              categories: ["discrimination", "harassment"],
              startPosition: 523,
              endPosition: 778,
              customFields: {
                enforcement: "EEOC",
              },
              children: [],
            },
          ],
        },
      ],
    },
    {
      id: "section-employer-obligations",
      title: "Employer Obligations and Compliance",
      categories: ["employer", "obligations", "compliance"],
      startPosition: 780,
      endPosition: 1530,
      customFields: {
        importance: "high",
        lastUpdated: "2024-01-15",
      },
      children: [
        {
          id: "subsection-compliance-requirements",
          title: "Compliance Requirements",
          categories: ["compliance", "regulations"],
          startPosition: 825,
          endPosition: 1242,
          customFields: {
            penaltyLevel: "severe",
            reviewFrequency: "quarterly",
          },
          children: [
            {
              id: "subsection-worker-classification",
              title: "Worker Classification",
              categories: ["classification", "tax"],
              startPosition: 1047,
              endPosition: 1162,
              customFields: {},
              children: [],
            },
            {
              id: "subsection-record-keeping",
              title: "Record Keeping",
              categories: ["records", "documentation"],
              startPosition: 1164,
              endPosition: 1242,
              customFields: {},
              children: [],
            },
          ],
        },
        {
          id: "subsection-safety-standards",
          title: "Safety Standards",
          categories: ["safety", "OSHA", "workplace"],
          startPosition: 1244,
          endPosition: 1530,
          customFields: {
            regulator: "OSHA",
            inspectionCycle: "annual",
          },
          children: [
            {
              id: "subsection-osha-compliance",
              title: "OSHA Compliance",
              categories: ["OSHA", "compliance"],
              startPosition: 1404,
              endPosition: 1481,
              customFields: {},
              children: [],
            },
            {
              id: "subsection-hazard-communication",
              title: "Hazard Communication",
              categories: ["hazards", "communication"],
              startPosition: 1483,
              endPosition: 1530,
              customFields: {},
              children: [],
            },
          ],
        },
      ],
    },
    {
      id: "section-employment-termination",
      title: "Employment Termination",
      categories: ["employment", "termination"],
      startPosition: 1532,
      endPosition: 1876,
      customFields: {},
      children: [
        {
          id: "subsection-at-will-employment",
          title: "At-Will Employment",
          categories: ["at-will", "termination"],
          startPosition: 1575,
          endPosition: 1779,
          customFields: {},
          children: [],
        },
        {
          id: "subsection-wrongful-termination",
          title: "Wrongful Termination",
          categories: ["wrongful", "termination"],
          startPosition: 1781,
          endPosition: 1876,
          customFields: {},
          children: [],
        },
      ],
    },
    {
      id: "section-leave-policies",
      title: "Leave Policies",
      categories: ["leave", "policies"],
      startPosition: 1878,
      endPosition: 2167,
      customFields: {},
      children: [
        {
          id: "subsection-fmla",
          title: "Family and Medical Leave Act (FMLA)",
          categories: ["FMLA", "leave"],
          startPosition: 1913,
          endPosition: 2064,
          customFields: {},
          children: [],
        },
        {
          id: "subsection-paid-sick-leave",
          title: "Paid Sick Leave",
          categories: ["sick-leave", "paid-leave"],
          startPosition: 2066,
          endPosition: 2167,
          customFields: {},
          children: [],
        },
      ],
    },
  ],
};
