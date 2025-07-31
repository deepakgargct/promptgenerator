import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

# Load embedding model once
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

# --- Search Prompts Only ---
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

# --- Initialize session state ---
if "confirmed_keywords" not in st.session_state:
    st.session_state.confirmed_keywords = []
if "keyword_input_raw" not in st.session_state:
    st.session_state.keyword_input_raw = ""

# --- UI: Step 1 - Keyword Input ---
st.title("🔍 Keyword Prompt Generator + Intent + Clustering")
st.markdown("Enter up to 20 keywords. Confirm intent, generate search-style prompts, and export as CSV.")

st.subheader("📝 Step 1: Enter Keywords")
st.session_state.keyword_input_raw = st.text_area(
    "Enter one keyword per line:",
    value=st.session_state.keyword_input_raw,
    height=200
)

if st.button("✅ Confirm Keywords"):
    confirmed = [kw.strip() for kw in st.session_state.keyword_input_raw.splitlines() if kw.strip()]
    if len(confirmed) > 20:
        st.error("❌ Only up to 20 keywords are allowed.")
    elif len(confirmed) == 0:
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        st.session_state.confirmed_keywords = confirmed
        for kw in confirmed:
            st.session_state[f"intent_{kw}"] = detect_intent(kw)

# --- Reset Button ---
if st.button("🔄 Reset All"):
    st.session_state.keyword_input_raw = ""
    st.session_state.confirmed_keywords = []
    for k in list(st.session_state.keys()):
        if k.startswith("intent_"):
            del st.session_state[k]
    st.experimental_rerun()

keywords = st.session_state.confirmed_keywords

# --- Step 2: Override Intent ---
if keywords:
    st.subheader("🧠 Step 2: Review or Override Intent")

    selected_intents = {}
    for kw in keywords:
        key_id = f"intent_{kw}"
        selected_intents[kw] = st.selectbox(
            f"Intent for `{kw}`:",
            ["product", "service", "blog"],
            index=["product", "service", "blog"].index(st.session_state.get(key_id, "blog")),
            key=key_id
        )

    if st.button("🚀 Generate Prompts + Cluster"):
        embeddings = model.encode(keywords)
        n_clusters = min(len(keywords), 4)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        cluster_labels = kmeans.fit_predict(embeddings)

        rows = []
        for i, kw in enumerate(keywords):
            intent = selected_intents[kw]
            search_prompts = generate_search_prompts(kw, intent)
            for prompt in search_prompts:
                rows.append({
                    "Keyword": kw,
                    "Intent": intent,
                    "Cluster": f"Cluster {cluster_labels[i]+1}",
                    "Prompt": prompt
                })

        df = pd.DataFrame(rows)
        st.success("✅ Prompt generation complete.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "keyword_prompts.csv", "text/csv")
