import streamlit as st
import pandas as pd

# --- Heuristic Intent Detection ---
def detect_intent(keyword):
    keyword = keyword.lower()

    blog_phrases = ["how to", "what is", "why", "benefits", "tips", "guide", "tutorial", "examples", "explained"]
    product_terms = ["buy", "best", "cheap", "vs", "review", "under", "comparison", "top", "deals", "affordable"]
    service_terms = ["hire", "service", "repair", "agency", "consulting", "maintenance", "provider", "company", "freelancer", "near me"]

    for phrase in blog_phrases:
        if phrase in keyword:
            return "blog"

    if any(term in keyword.split() for term in service_terms):
        return "service"
    if any(term in keyword.split() for term in product_terms):
        return "product"

    # Fallbacks
    if "services" in keyword or "near me" in keyword:
        return "service"
    if "vs" in keyword or "best" in keyword:
        return "product"

    return "blog"

# --- Generate search-style prompts ---
def generate_search_prompts(keyword, intent):
    kw = keyword.lower()
    prompts = []

    if intent == "product":
        prompts = [
            f"best {kw} for beginners",
            f"{kw} reviews 2025",
            f"top 10 {kw} to consider",
            f"{kw} buying guide",
            f"{kw} vs alternatives",
            f"{kw} under $100",
            f"where to buy {kw} online",
            f"{kw} features and specifications",
            f"{kw} deals this month",
            f"is {kw} worth it in 2025",
        ]
    elif intent == "service":
        prompts = [
            f"{kw} service near me",
            f"how to hire a {kw}",
            f"top {kw} agencies in [your city]",
            f"{kw} pricing explained",
            f"questions to ask before hiring {kw}",
            f"{kw} for small businesses",
            f"best {kw} providers in 2025",
            f"how {kw} works",
            f"licensed {kw} experts near me",
            f"{kw} packages and offers",
        ]
    else:  # blog
        prompts = [
            f"how does {kw} work",
            f"what is {kw}",
            f"tips to improve your {kw}",
            f"{kw} guide for beginners",
            f"top benefits of {kw}",
            f"latest trends in {kw}",
            f"common myths about {kw}",
            f"{kw} explained simply",
            f"why {kw} is important in 2025",
            f"{kw} vs alternatives: what to know",
        ]
    
    return prompts

# --- Streamlit App UI ---
st.title("🔍 Keyword Intent Detector + Prompt Generator")
st.markdown("Enter up to 20 keywords. The app will detect the search **intent**, let you **override** it, and generate **search-style prompts**.")

user_input = st.text_area("✏️ Enter keywords (one per line, max 20):", height=200)
submit = st.button("🚀 Generate Prompts")

if submit:
    keywords = [kw.strip() for kw in user_input.splitlines() if kw.strip()]

    if not keywords:
        st.warning("Please enter at least one keyword.")
    elif len(keywords) > 20:
        st.error("Limit is 20 keywords.")
    else:
        final_prompts = []

        st.subheader("🧠 Keyword Intent Review & Override")

        selected_intents = {}
        for kw in keywords:
            default_intent = detect_intent(kw)
            selected_intents[kw] = st.selectbox(
                f"Select intent for: `{kw}`",
                options=["product", "service", "blog"],
                index=["product", "service", "blog"].index(default_intent)
            )

        # Generate prompts after intent review
        if st.button("✅ Confirm & Generate Prompts"):
            for kw in keywords:
                intent = selected_intents[kw]
                prompts = generate_search_prompts(kw, intent)
                for p in prompts:
                    final_prompts.append({
                        "Keyword": kw,
                        "Intent": intent,
                        "Search Prompt": p
                    })

            df = pd.DataFrame(final_prompts)
            st.success("🎉 Prompts generated!")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="keyword_prompts.csv",
                mime="text/csv"
            )
