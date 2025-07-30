import { NextRequest, NextResponse } from "next/server";
import { Client } from "@opensearch-project/opensearch";
import { appConfig } from "@/config/appConfig";

const client = new Client({
  node: appConfig.OPENSEARCH.URL,
  auth: {
    username: appConfig.OPENSEARCH.USER,
    password: appConfig.OPENSEARCH.PASS,
  },
  ssl: {
    rejectUnauthorized: appConfig.OPENSEARCH.VERIFY_CERTS,
  },
});

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const {
      indexName,
      query,
      searchMode,
      dateRange,
      batchNumber,
      sort,
      page = 1,
      size = 10,
    } = body;

    if (!indexName || !query) {
      return NextResponse.json(
        { message: "Index name and query are required." },
        { status: 400 }
      );
    }

    const mustClauses: any[] = [];

    if (searchMode === "exact") {
      mustClauses.push({ match_phrase: { text: query } });
    } else {
      mustClauses.push({
        match: {
          text: {
            query,
            operator: searchMode === "all" ? "and" : "or",
            fuzziness: 1,
          },
        },
      });
    }

    const filterClauses: any[] = [];

    if (dateRange?.from && dateRange?.to) {
      filterClauses.push({
        range: {
          timestamp: {
            gte: dateRange.from,
            lte: dateRange.to,
          },
        },
      });
    }

    if (batchNumber) {
      filterClauses.push({
        term: { batch_number: batchNumber },
      });
    }

    const sortClauses: any[] = [];
    if (sort.by === "date") {
      sortClauses.push({ timestamp: { order: sort.order } });
    } else {
      sortClauses.push({ _score: { order: "desc" } });
    }

    const from = (page - 1) * size;

    const searchResponse = await client.search({
      index: indexName,
      body: {
        query: {
          bool: {
            must: mustClauses,
            filter: filterClauses,
          },
        },
        highlight: {
          fields: {
            text: {
              fragment_size: 999999999,
              number_of_fragments: 1,
            },
          },
          pre_tags: ["<em>"],
          post_tags: ["</em>"],
        },
        sort: sortClauses,
        from,
        size,
      },
    });

    return NextResponse.json(searchResponse.body);
  } catch (error: any) {
    console.error("OpenSearch Error:", error);
    return NextResponse.json(
      {
        message: "An error occurred during the search.",
        error: error.message || "Unknown error",
      },
      { status: 500 }
    );
  }
}
