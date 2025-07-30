import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import {
  Card,
  CardContent,
  CardHeader,
  CardFooter,
  CardTitle,
} from "@/components/ui/card";
import { FileUp, Book } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Hit } from "@/types/opensearch";
import { convertS3ToHttps } from "@/lib/stores/s3";

interface ResultCardProps {
  hit: Hit;
}

const sanitizeContent = (rawContent: string) => {
  let cleanedContent = rawContent
    .replace(/^\."\s+/, "")
    .replace(/\n{2,}/g, "\n")
    .trimStart();
  return cleanedContent;
};

const ResultCard: React.FC<ResultCardProps> = ({ hit }) => {
  const { _source: source, highlight } = hit;

  const contextTitle = [source.title, source.chapter, source.header]
    .filter(Boolean)
    .join(" / ");

  const rawContent = highlight?.text
    ? highlight.text.join(" ... ")
    : source.text ?? "*No content available*";

  // Sanitize markdown content before rendering
  const contentToRender = sanitizeContent(rawContent);

  // console.log(contentToRender);

  // State to hold resolved S3 link string
  const [resolvedS3Link, setResolvedS3Link] = useState<string>("");

  useEffect(() => {
    let isMounted = true;
    async function fetchS3Link() {
      try {
        if (source.s3_link && source.page_number !== undefined) {
          const url = await convertS3ToHttps(
            source.s3_link,
            source.page_number
          );
          if (isMounted) setResolvedS3Link(url);
        } else {
          if (isMounted) setResolvedS3Link("");
        }
      } catch {
        if (isMounted) setResolvedS3Link("");
      }
    }
    fetchS3Link();
    return () => {
      isMounted = false;
    };
  }, [source.s3_link, source.page_number]);

  return (
    <Card className="overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <CardHeader className="bg-muted/50 border-b p-4">
        <CardTitle className="text-base font-semibold text-foreground flex items-center">
          {source.title && <Book className="mr-2 h-4 w-4 text-primary" />}
          {contextTitle || "Document Chunk"}
        </CardTitle>
      </CardHeader>

      <CardContent className="px-6">
        <div className="prose prose-base prose-headings:text-foreground max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
            skipHtml={false}
            components={{
              ul: ({ node, ...props }) => (
                <ul className="list-disc list-inside my-2" {...props} />
              ),
              ol: ({ node, ...props }) => (
                <ol className="list-decimal list-inside my-2" {...props} />
              ),
              li: ({ node, ...props }) => <li className="mb-1" {...props} />,
              strong: ({ node, ...props }) => (
                <strong className="font-semibold text-foreground" {...props} />
              ),
              p: ({ node, ...props }) => (
                <p className="my-1 text-foreground" {...props} />
              ),
            }}
          >
            {contentToRender}
          </ReactMarkdown>
        </div>
      </CardContent>

      <CardFooter className="bg-muted/50 p-3 flex justify-between items-center">
        <div className="text-xs text-muted-foreground">
          <span>Word Count: {source.word_count}</span> |{" "}
          <span>Batch: {source.batch_number}</span>
        </div>

        {resolvedS3Link ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <a
                  href={resolvedS3Link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex"
                >
                  <Badge
                    variant="secondary"
                    className="hover:bg-primary/20 transition-colors"
                  >
                    <FileUp className="mr-2 h-3 w-3" />
                    Page: {source.page_number}
                  </Badge>
                </a>
              </TooltipTrigger>
              <TooltipContent>
                <p>Open original document at page {source.page_number}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : (
          <Badge variant="secondary" className="opacity-50 cursor-not-allowed">
            <FileUp className="mr-2 h-3 w-3" />
            Page: {source.page_number}
          </Badge>
        )}
      </CardFooter>
    </Card>
  );
};

const badgeVariants = {
  secondary: "bg-muted text-muted-foreground border border-border",
  primary: "bg-primary text-primary-foreground border border-primary",
};

const Badge: React.FC<{
  variant?: keyof typeof badgeVariants;
  className?: string;
  children: React.ReactNode;
}> = ({ className = "", variant = "secondary", children }) => (
  <div
    className={`text-xs inline-flex items-center rounded-full px-2.5 py-0.5 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${badgeVariants[variant]} ${className}`}
  >
    {children}
  </div>
);

export default ResultCard;
