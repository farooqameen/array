import { OpenSearchResult } from "@/types/opensearch";
import { useState, useEffect, useCallback } from "react";
import { DateRange } from "react-day-picker";

export const useSearch = (indexName: string) => {
  const [query, setQuery] = useState("");
  const [searchMode, setSearchMode] = useState<"any" | "all" | "exact">("any");
  const [dateRange, setDateRange] = useState<DateRange | undefined>();
  const [batchNumber, setBatchNumber] = useState("");
  const [sort, setSort] = useState<{
    by: "relevance" | "date";
    order: "asc" | "desc";
  }>({ by: "relevance", order: "desc" });

  const [results, setResults] = useState<OpenSearchResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 10;

  const executeQuery = useCallback(
    async (page = 1) => {
      if (!query.trim()) {
        setResults(null);
        return;
      }

      setIsLoading(true);
      setError(null);
      setCurrentPage(page);

      try {
        const response = await fetch("/routes/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            indexName,
            query,
            searchMode,
            dateRange,
            batchNumber,
            sort,
            page,
            size: resultsPerPage,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || "Search request failed");
        }

        const data: OpenSearchResult = await response.json();
        setResults(data);
      } catch (err: any) {
        setError(err.message || "An error occurred");
        setResults(null);
      } finally {
        setIsLoading(false);
      }
    },
    [indexName, query, searchMode, dateRange, batchNumber, sort, resultsPerPage]
  );

  useEffect(() => {
    if (query) executeQuery(1);
  }, [sort, dateRange, batchNumber]);

  const pagination = {
    currentPage,
    totalPages: results
      ? Math.ceil(results.hits.total.value / resultsPerPage)
      : 0,
    hasPrevPage: currentPage > 1,
    hasNextPage: results
      ? currentPage < Math.ceil(results.hits.total.value / resultsPerPage)
      : false,
  };

  const setPage = (page: number) => {
    if (page > 0 && page <= pagination.totalPages) {
      executeQuery(page);
    }
  };

  return {
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
  };
};
