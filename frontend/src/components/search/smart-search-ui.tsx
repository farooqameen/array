import React from "react";
import { useSearch } from "@/hooks/useSearch";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Search,
  ListFilter,
  ArrowDownUp,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  FileText,
  CalendarDays,
  Hash,
} from "lucide-react";

import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { DateRangePicker } from "./date-range-picker";
import SkeletonLoader from "./skeleton-loader";
import ResultCard from "./result-card";

interface SmartSearchUIProps {
  indexName: string;
  onBack: () => void;
}

const SmartSearchUI: React.FC<SmartSearchUIProps> = ({ indexName, onBack }) => {
  const {
    query,
    setQuery,
    searchMode,
    setSearchMode,
    dateRange,
    setDateRange,
    batchNumber,
    setBatchNumber,
    sort,
    setSort,
    results,
    isLoading,
    error,
    pagination,
    setPage,
    executeQuery,
  } = useSearch(indexName);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    executeQuery();
  };

  const renderPagination = () => {
    if (!pagination.totalPages || pagination.totalPages <= 1) return null;

    const pageNumbers = [];
    const maxPagesToShow = 5;
    const startPage = Math.max(
      1,
      pagination.currentPage - Math.floor(maxPagesToShow / 2)
    );
    const endPage = Math.min(
      pagination.totalPages,
      startPage + maxPagesToShow - 1
    );

    for (let i = startPage; i <= endPage; i++) {
      pageNumbers.push(i);
    }

    return (
      <div className="flex items-center justify-center space-x-2 mt-8">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setPage(1)}
                disabled={pagination.currentPage === 1}
              >
                <ChevronsLeft className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>First Page</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setPage(pagination.currentPage - 1)}
                disabled={!pagination.hasPrevPage}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Previous Page</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        {pageNumbers.map((page) => (
          <Button
            key={page}
            variant={pagination.currentPage === page ? "default" : "outline"}
            onClick={() => setPage(page)}
          >
            {page}
          </Button>
        ))}

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setPage(pagination.currentPage + 1)}
                disabled={!pagination.hasNextPage}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Next Page</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setPage(pagination.totalPages)}
                disabled={pagination.currentPage === pagination.totalPages}
              >
                <ChevronsRight className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Last Page</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    );
  };

  return (
    <div className="container mx-auto p-4 md:p-6 lg:p-8 min-h-screen">
      <Button variant="ghost" onClick={onBack} className="mb-4 pl-0">
        <ChevronLeft className="mr-2 h-4 w-4" /> Back to Index Selection
      </Button>
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Smart Search</CardTitle>
          <CardDescription>
            Querying index:{" "}
            <span className="font-semibold text-primary">{indexName}</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Query and Search Mode */}
          <form
            onSubmit={handleSearch}
            className="flex flex-col md:flex-row items-start gap-4 mb-6"
          >
            <div className="relative flex-grow w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search within documents..."
                className="pl-10 h-12 text-base"
              />
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="submit"
                    size="lg"
                    className="h-12 w-full md:w-auto"
                  >
                    Search
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Execute Search</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </form>

          {/* Controls: Filters, Sorting, and Search Mode */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Search Mode */}
            <div className="space-y-3">
              <Label className="font-semibold">Search Mode</Label>
              <TooltipProvider>
                <RadioGroup
                  value={searchMode}
                  onValueChange={(v: any) => setSearchMode(v as any)}
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="any" id="any" />
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Label htmlFor="any" className="cursor-pointer">
                          At least one word
                        </Label>
                      </TooltipTrigger>
                      <TooltipContent>
                        Returns documents with any of the query terms.
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="all" id="all" />
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Label htmlFor="all" className="cursor-pointer">
                          All words
                        </Label>
                      </TooltipTrigger>
                      <TooltipContent>
                        Returns documents containing all query terms.
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="exact" id="exact" />
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Label htmlFor="exact" className="cursor-pointer">
                          Precise phrase
                        </Label>
                      </TooltipTrigger>
                      <TooltipContent>
                        Returns documents with the exact query phrase.
                      </TooltipContent>
                    </Tooltip>
                  </div>
                </RadioGroup>
              </TooltipProvider>
            </div>

            {/* Filters */}
            <div className="space-y-3">
              <Label className="font-semibold flex items-center">
                <ListFilter className="mr-2 h-4 w-4" />
                Filters
              </Label>
              <div className="grid gap-4">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="relative">
                        <CalendarDays className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <DateRangePicker
                          date={dateRange}
                          onDateChange={setDateRange}
                        />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      Filter results by date range using the 'timestamp' field.
                    </TooltipContent>
                  </Tooltip>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="relative">
                        <Hash className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                          type="text"
                          placeholder="Batch Number"
                          value={batchNumber}
                          onChange={(e) => setBatchNumber(e.target.value)}
                          className="pl-9"
                        />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      Filter by the 'batch_number' field.
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>

            {/* Sorting */}
            <div className="space-y-3">
              <Label className="font-semibold flex items-center">
                <ArrowDownUp className="mr-2 h-4 w-4" />
                Sort By
              </Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full justify-between"
                        >
                          <span>
                            {sort.by === "relevance" ? "Relevance" : "Date"}
                            {sort.by === "date" &&
                              ` (${sort.order === "asc" ? "Asc" : "Desc"})`}
                          </span>
                          <ArrowDownUp className="ml-2 h-4 w-4 text-muted-foreground" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent className="w-56">
                        <DropdownMenuLabel>Sort Options</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onSelect={() =>
                            setSort({ by: "relevance", order: "desc" })
                          }
                        >
                          Relevance
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onSelect={() =>
                            setSort({ by: "date", order: "desc" })
                          }
                        >
                          Date (Newest First)
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onSelect={() => setSort({ by: "date", order: "asc" })}
                        >
                          Date (Oldest First)
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TooltipTrigger>
                  <TooltipContent>
                    Change the sort order of the results.
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>

          {/* Results Area */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Results
            </h3>
            {isLoading ? (
              <SkeletonLoader />
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-destructive font-semibold">
                  An error occurred:
                </p>
                <p className="text-muted-foreground mt-2">{error}</p>
                <Button onClick={() => executeQuery()} className="mt-4">
                  Retry
                </Button>
              </div>
            ) : results && results.hits.total.value > 0 ? (
              <>
                <p className="text-sm text-muted-foreground mb-4">
                  Showing {results.hits.hits.length} of{" "}
                  {results.hits.total.value} total results.
                </p>
                <div className="grid gap-6">
                  {results.hits.hits.map((hit: any) => (
                    <ResultCard key={hit._id} hit={hit} />
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground">
                  {query
                    ? "No results found for your query."
                    : "Enter a query to see results."}
                </p>
              </div>
            )}
          </div>
          {renderPagination()}
        </CardContent>
      </Card>
    </div>
  );
};

export default SmartSearchUI;
