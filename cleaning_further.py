import pandas as pd
import re

def clean_author(author_str):
    """
    Clean a single 'author' string with the rules:
      1) If there are no parentheses in a token, keep it as-is.
      2) If there are parentheses, keep the token only if it has the word 'Author' (case-insensitive) in them.
         e.g. 'Heidi Murkoff (Author, Narrator)' -> keep
              'Michael Beck (Narrator)' -> remove
      3) Do not split on commas that are inside parentheses.
         So 'Robert Iger (Author, Narrator)' remains one token.
    """
    # Handle NaN or empty
    if not isinstance(author_str, str) or not author_str.strip():
        return ""

    # We'll parse the string character-by-character.
    # We'll treat commas at the "top level" (outside parentheses) as separators,
    # but ignore commas that occur inside parentheses.
    tokens = []
    bracket_level = 0
    current_token = []

    for ch in author_str:
        if ch == '(':
            bracket_level += 1
            current_token.append(ch)
        elif ch == ')':
            bracket_level = max(0, bracket_level - 1)
            current_token.append(ch)
        elif ch == ',' and bracket_level == 0:
            # We hit a top-level comma, so finalize the current token
            token_str = "".join(current_token).strip()
            if token_str:
                tokens.append(token_str)
            current_token = []
        else:
            current_token.append(ch)

    # Add the last token if there is one
    if current_token:
        token_str = "".join(current_token).strip()
        if token_str:
            tokens.append(token_str)

    # Now filter the tokens
    valid_tokens = []
    for t in tokens:
        # Case A: No parentheses at all -> keep
        if '(' not in t and ')' not in t:
            valid_tokens.append(t)
        else:
            # Case B: If it has parentheses, keep only if '(Author' is inside
            # (case-insensitive). This will allow something like (Author, Narrator).
            if re.search(r'\(.*author.*\)', t, flags=re.IGNORECASE):
                valid_tokens.append(t)

    return ", ".join(valid_tokens)

# -------------------------------
# Example usage
# -------------------------------

df = pd.read_csv("Amazon_books_cleaned.csv")

cleaned_authors = []
for idx, row in df.iterrows():
    original_author = row.get("author", "")
    title = row.get("title", f"Row_{idx}")

    cleaned = clean_author(original_author)

    # If cleaning yields an empty string, print line number & title
    if not cleaned.strip():
        print(f"Line {idx} is empty after cleaning. Title: {title}")

    cleaned_authors.append(cleaned)

df["author"] = cleaned_authors

# Optional: save the cleaned DataFrame
df.to_csv("Amazon_books_cleaned_output.csv", index=False)

print(df[["title", "author"]].head(20))
