import streamlit as st
import pandas as pd

# --- Intent Detection (Rule-based placeholder) ---
def detect_intent(keyword):
    keyword = keyword.lower()
    product_triggers = ["buy", "best", "cheap", "under", "vs", "reviews"]
    service_triggers = ["hire", "service", "near me", "repair", "agency"]
    blog_triggers = ["how", "what", "why", "tips", "guide", "benefits"]

    # Heuristic fallback
    if any(term in keyword for term in product_triggers):
        return "product"
    elif any(term in keyword for term in service_triggers):
        return "service"
    elif any(term in keyword for term in blog_triggers):
        return "blog"
    else:
        return "blog"

# --- Generate Search-Style Prompts ---
def generate_search_prompts(keyword, intent):
    prompts = []
    kw = keyword.lower()

    if intent == "product":
        prompts = [
            f"best {kw} for daily use",
            f"affordable {kw} under $100",
            f"{kw} reviews 2025",
            f"{kw} vs alternatives",
            f"top rated {kw} on Amazon",
            f"where to buy {kw} online",
            f"cheap {kw} deals today",
            f"is {kw} worth the money",
            f"{kw} buying guide",
            f"{kw} for beginners",
        ]

    elif intent == "service":
        prompts = [
            f"{kw} service near me",
            f"how to hire {kw}",
            f"top-rated {kw} company in [city]",
            f"{kw} cost breakdown 2025",
            f"licensed {kw} professionals near me",
            f"affordable {kw} providers",
            f"what to ask before hiring {kw}",
            f"{kw} emergency support",
            f"local {kw} contractors",
            f"{kw} for small businesses",
        ]

    elif intent == "blog":
        prompts = [
            f"how does {kw} work",
            f"what is the benefit of {kw}",
            f"ways to improve your {kw}",
            f"{kw} explained for beginners",
            f"top 10 tips about {kw}",
            f"latest research on {kw}",
            f"myths and facts about {kw}",
            f"why {kw} matters in 2025",
            f"guide to understanding {kw}",
            f"{kw} in everyday life",
        ]

    return prompts

# --- Streamlit App ---
st.title("🔎 User Search Prompt Generator by Keyword Intent")
st.markdown("Upload or paste up to 20 keywords to generate prompts simulating **real search behavior**.")

input_keywords = st.text_area("Enter one keyword per line (max 20):", height=200)
submit = st.button("🔍 Generate Search Prompts")

if submit:
    keywords = [k.strip() for k in input_keywords.splitlines() if k.strip()]
    
    if not keywords:
        st.warning("❗ Please enter at least one keyword.")
    elif len(keywords) > 20:
        st.error("🚫 Maximum 20 keywords allowed.")
    else:
        all_prompts = []

        for kw in keywords:
            intent = detect_intent(kw)
            prompts = generate_search_prompts(kw, intent)

            for p in prompts:
                all_prompts.append({
                    "Keyword": kw,
                    "Intent": intent,
                    "Search Prompt": p
                })

        df = pd.DataFrame(all_prompts)
        st.success("✅ Prompts generated successfully.")
        st.dataframe(df)

        # Export to CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Prompts as CSV",
            csv,
            "search_prompts.csv",
            "text/csv"
        )
