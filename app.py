import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

# Load model once
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# --- Intent Detection ---
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
    if "services" in keyword or "near me" in keyword:
        return "service"
    if "vs" in keyword or "best" in keyword:
        return "product"
    return "blog"

# --- Search Prompts ---
def generate_search_prompts(keyword, intent):
    kw = keyword.lower()
    if intent == "product":
        return [
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
        return [
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
        return [
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

# --- AI Prompts ---
def generate_ai_prompts(keyword, intent):
    if intent == "product":
        return [
            f"Act as an ecommerce copywriter and write a product description for '{keyword}'.",
            f"Create a comparison table for '{keyword}' vs alternatives.",
            f"List top 5 use-cases for '{keyword}' and write example product blurbs.",
        ]
    elif intent == "service":
        return [
            f"Act as a local SEO expert and create a service page for '{keyword}'.",
            f"Write a testimonial and case study summary for someone using '{keyword}'.",
            f"Explain the process and benefits of hiring a '{keyword}' service provider.",
        ]
    else:
        return [
            f"Write a blog post outline for the topic '{keyword}'.",
            f"Generate 5 FAQs about '{keyword}'.",
            f"Act as a subject expert and explain '{keyword}' to beginners.",
        ]

# --- App UI ---
st.title("🔍 Keyword Intent → Prompt Generator + Clustering")
st.markdown("Paste up to **20 keywords** below. We'll detect or let you override the search **intent**, then generate **prompts** and cluster keywords.")

keywords_raw = st.text_area("🔤 Enter keywords (one per line):", height=200)
keywords = [kw.strip() for kw in keywords_raw.splitlines() if kw.strip()]

# Reset Button
if st.button("🔄 Reset Intents"):
    for kw in keywords:
        st.session_state.pop(f"intent_{kw}", None)
    st.success("Session intents reset.")

# Proceed only if keywords are entered
if keywords:
    if len(keywords) > 20:
        st.error("🚫 Max 20 keywords allowed.")
        st.stop()

    st.subheader("🧠 Step 1: Intent Detection & Override")

    # Collect intent (default or user-selected)
    selected_intents = {}
    for kw in keywords:
        key_id = f"intent_{kw}"
        if key_id not in st.session_state:
            st.session_state[key_id] = detect_intent(kw)
        selected_intents[kw] = st.selectbox(
            f"Intent for `{kw}`:",
            ["product", "service", "blog"],
            index=["product", "service", "blog"].index(st.session_state[key_id]),
            key=key_id
        )

    if st.button("✅ Generate Prompts + Cluster"):
        embeddings = model.encode(keywords)
        n_clusters = min(len(keywords), 4)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        cluster_labels = kmeans.fit_predict(embeddings)

        rows = []
        for i, kw in enumerate(keywords):
            intent = selected_intents[kw]
            search_prompts = generate_search_prompts(kw, intent)
            ai_prompts = generate_ai_prompts(kw, intent)
            for prompt in search_prompts + ai_prompts:
                rows.append({
                    "Keyword": kw,
                    "Intent": intent,
                    "Cluster": f"Cluster {cluster_labels[i]+1}",
                    "Prompt Type": "Search" if prompt in search_prompts else "AI",
                    "Prompt": prompt
                })

        df = pd.DataFrame(rows)
        st.success("🎉 Prompt generation complete.")
        st.dataframe(df)

        # Export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "keyword_prompts.csv", "text/csv")
