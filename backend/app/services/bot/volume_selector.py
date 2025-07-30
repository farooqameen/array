import re

from llama_index.core.settings import Settings

from .volume_metadata import VOLUMES


def score_volumes_with_llm(query, beam_width):
    """
    Use the LlamaIndex LLM model (as configured in settings) to score each volume for relevance to the query.
    Returns the top-k (beam_width) volumes.
    """
    llm = Settings.llm
    scored_volumes = []
    for volume in VOLUMES:
        prompt = (
            f"You are Claude, an expert legal assistant.\n"
            f"User query: {query}\n"
            f"Volume: {volume['name']}\n"
            f"Description: {volume['description']}\n"
            """
            FORMAT YOUR RESPONSE EXACTLY LIKE SO:
            [Your score here (this line is to be excluded from your response) ]

            [CRITICAL: Respond with a score between 0.0 and 1.0, where 1.0 means the query's subject is mntioned in the volume name or description, and 0.0 means it is extremely unlikely to be found in the volume. (this line is to be excluded from your response)]
            """
        )
        response = llm.complete(prompt)
        # logger.info(response)
        match = re.search(r"\d*\.?\d+", response.text)
        score = float(match.group()) if match else 0.0
        scored_volumes.append((volume, score))
        for v, s in scored_volumes:
            if s == 1.0:
                for v, s in scored_volumes:
                    if s <= 0.7:
                        scored_volumes.remove((v, s))
    scored_volumes.sort(key=lambda x: x[1], reverse=True)

    return scored_volumes[:beam_width]
