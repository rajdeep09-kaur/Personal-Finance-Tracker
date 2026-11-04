import json
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------- Configuration ----------------------------

st.set_page_config(
    page_title="Personal Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path("finance_data.csv")
BUDGET_FILE = Path("monthly_budgets.json")
COLUMNS = ["date", "amount", "category", "description"]
DATE_FORMAT = "%d-%m-%Y"
CURRENCY = "₹"


def _stretch_kwargs():
    """Use width='stretch' on new Streamlit, use_container_width on older ones."""
    try:
        major, minor = (int(p) for p in st.__version__.split(".")[:2])
        if (major, minor) >= (1, 50):
            return {"width": "stretch"}
    except ValueError:
        pass
    return {"use_container_width": True}


STRETCH = _stretch_kwargs()


# ---------------------------- Styling ----------------------------

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

      :root {
        --ink: #18372d;
        --muted: #718078;
        --green: #176448;
        --green-dark: #103f32;
        --mint: #eaf5ef;
        --surface: #ffffff;
        --line: #e3ece6;
      }

      html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
      }

      .stApp {
        background: #f4f7f5;
        color: var(--ink);
      }

      .block-container {
        max-width: 1460px;
        padding-top: 2.1rem;
        padding-bottom: 3rem;
      }

      /* Sidebar */
      [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #eaf5ef 0%, #f4faf6 100%) !important;
        border-right: 1px solid #dce9e1 !important;
      }

      [data-testid="stSidebar"] > div:first-child {
        padding: 1.35rem 1rem;
      }

      [data-testid="stSidebar"] h2 {
        color: var(--green-dark) !important;
        font-size: 1.25rem;
        font-weight: 800;
      }

      [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] label,
      [data-testid="stSidebar"] span {
        color: #365b4b !important;
      }

      [data-testid="stSidebar"] [data-testid="stRadio"] > label {
        font-weight: 700;
        color: var(--green-dark) !important;
        margin-bottom: .55rem;
      }

      [data-testid="stSidebar"] [role="radiogroup"] {
        gap: .35rem;
      }

      [data-testid="stSidebar"] [role="radiogroup"] label {
        background: rgba(255,255,255,.68);
        border: 1px solid #e0ece4;
        border-radius: 11px;
        padding: .55rem .7rem;
        transition: all .15s ease;
      }

      [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: #dcefe3;
        border-color: #b9d8c5;
      }

      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #668071 !important;
      }

      /* Hero banner */
      .hero {
        background: linear-gradient(115deg, #103f32 0%, #176448 58%, #27815e 100%);
        padding: 2rem 2.15rem;
        border-radius: 22px;
        color: #ffffff;
        margin-bottom: 1.65rem;
        box-shadow: 0 12px 30px rgba(16, 63, 50, .13);
        position: relative;
        overflow: hidden;
      }

      .hero:after {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        border-radius: 50%;
        right: -55px;
        top: -105px;
        background: rgba(255,255,255,.07);
      }

      .hero h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 2.05rem;
        font-weight: 800;
        letter-spacing: -.04em;
      }

      .hero p {
        color: #d9eee3 !important;
        margin: .55rem 0 0 0;
        font-size: .98rem;
      }

      h1, h2, h3, h4 {
        color: var(--ink) !important;
        letter-spacing: -.02em;
      }

      h3 {
        font-weight: 750;
      }

      [data-testid="stMarkdownContainer"] p {
        color: #52665b;
      }

      /* KPI cards */
      .metric-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.25rem 1.3rem;
        min-height: 132px;
        box-shadow: 0 5px 18px rgba(25, 65, 45, .045);
        transition: transform .15s ease, box-shadow .15s ease;
      }

      .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(25, 65, 45, .08);
      }

      .metric-label {
        color: #62756a;
        font-size: .88rem;
        font-weight: 700;
      }

      .metric-value {
        color: #153e30;
        font-size: 1.8rem;
        font-weight: 800;
        margin-top: .45rem;
        letter-spacing: -.035em;
      }

      .metric-note {
        color: #829188;
        font-size: .78rem;
        margin-top: .25rem;
      }

      .section-title {
        color: var(--ink);
        font-weight: 800;
        font-size: 1.08rem;
        margin: .55rem 0 .8rem 0;
      }

      /* Inputs, alerts, tables and buttons */
      div[data-testid="stDateInput"] label,
      div[data-testid="stNumberInput"] label,
      div[data-testid="stSelectbox"] label,
      div[data-testid="stTextInput"] label {
        color: #365447 !important;
        font-weight: 650;
      }

      [data-testid="stTextInput"] input,
      [data-testid="stNumberInput"] input,
      [data-testid="stDateInput"] input,
      [data-testid="stSelectbox"] > div > div {
        background: #ffffff !important;
        border-color: #dce8e0 !important;
        border-radius: 10px !important;
        color: #18372d !important;
      }

      div[data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid #dce9e1;
      }

      div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        overflow: hidden;
        background: #ffffff;
      }

      div.stButton > button,
      div[data-testid="stFormSubmitButton"] button,
      [data-testid="stDownloadButton"] button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 2.65rem;
      }

      div.stButton > button[kind="primary"],
      div[data-testid="stFormSubmitButton"] button[kind="primary"] {
        background: #176448;
        border-color: #176448;
        color: #ffffff;
      }

      div.stButton > button[kind="primary"]:hover,
      div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
        background: #104d39;
        border-color: #104d39;
      }

      [data-testid="stProgressBar"] > div > div {
        background: #23845e;
      }

      /* Force readable form controls even if the browser/Streamlit is in dark mode */
      div[data-baseweb="select"] > div,
      div[data-baseweb="input"],
      div[data-baseweb="base-input"],
      [data-testid="stDateInput"] div[data-baseweb="input"] {
        background: #ffffff !important;
        border-color: #dce8e0 !important;
        border-radius: 10px !important;
      }

      div[data-baseweb="select"] *,
      div[data-baseweb="input"] input,
      div[data-baseweb="base-input"] input,
      [data-testid="stNumberInput"] button {
        color: #18372d !important;
        -webkit-text-fill-color: #18372d !important;
      }

      div[data-baseweb="select"] svg,
      [data-testid="stDateInput"] svg,
      [data-testid="stNumberInput"] button svg {
        fill: #18372d !important;
        color: #18372d !important;
      }

      input::placeholder {
        color: #8a9a91 !important;
        -webkit-text-fill-color: #8a9a91 !important;
        opacity: 1 !important;
      }

      /* Dropdown menu (rendered in a popover outside the main page) */
      div[data-baseweb="popover"] ul,
      div[data-baseweb="popover"] li,
      div[data-baseweb="popover"] [role="option"] {
        background: #ffffff !important;
        color: #18372d !important;
      }

      div[data-baseweb="popover"] li:hover,
      div[data-baseweb="popover"] [role="option"]:hover {
        background: #eaf5ef !important;
      }

      /* Primary buttons (covers newer Streamlit test ids) */
      button[kind="primary"],
      button[data-testid="stBaseButton-primary"],
      button[data-testid="stBaseButton-primaryFormSubmit"] {
        background: #176448 !important;
        border-color: #176448 !important;
        color: #ffffff !important;
      }

      button[kind="primary"] *,
      button[data-testid="stBaseButton-primary"] *,
      button[data-testid="stBaseButton-primaryFormSubmit"] * {
        color: #ffffff !important;
      }

      button[kind="primary"]:hover,
      button[data-testid="stBaseButton-primary"]:hover,
      button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background: #104d39 !important;
        border-color: #104d39 !important;
      }

      /* Transaction type dropdown: mint background, dark green bold text */
      .st-key-transaction_type div[data-baseweb="select"] > div {
        background: #eaf5ef !important;
        border: 1.5px solid #176448 !important;
        border-radius: 10px !important;
      }

      .st-key-transaction_type div[data-baseweb="select"] * {
        color: #103f32 !important;
        -webkit-text-fill-color: #103f32 !important;
        font-weight: 700 !important;
      }

      .st-key-transaction_type div[data-baseweb="select"] svg {
        fill: #176448 !important;
      }

      hr {
        border-color: #e1ebe4;
      }

      @media (max-width: 800px) {
        .block-container {
          padding: 1rem 1rem 2rem 1rem;
        }

        .hero {
          padding: 1.45rem;
          border-radius: 16px;
        }

        .hero h1 {
          font-size: 1.55rem;
        }

        .metric-value {
          font-size: 1.45rem;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------- Data helpers ----------------------------

def ensure_files():
    """Create the transaction CSV with the original four-column structure."""
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)


def load_transactions():
    ensure_files()

    try:
        df = pd.read_csv(DATA_FILE)
    except (pd.errors.EmptyDataError, UnicodeDecodeError):
        df = pd.DataFrame(columns=COLUMNS)

    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[COLUMNS].copy()

    df["date"] = pd.to_datetime(df["date"], format=DATE_FORMAT, errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["category"] = df["category"].astype(str).str.strip().str.title()
    df["description"] = df["description"].fillna("").astype(str)

    df = df.dropna(subset=["date", "amount"])
    df = df[(df["amount"] > 0) & df["category"].isin(["Income", "Expense"])]

    return df.sort_values("date", ascending=False).reset_index(drop=True)


def append_transaction(transaction_date, amount, category, description):
    """Append one row, making sure it never gets glued to an unterminated last line."""
    ensure_files()

    needs_newline = False
    with DATA_FILE.open("rb") as file:
        file.seek(-1, 2)
        needs_newline = file.read(1) not in (b"\n", b"\r")

    if needs_newline:
        with DATA_FILE.open("a", encoding="utf-8", newline="") as file:
            file.write("\n")

    row = pd.DataFrame([{
        "date": transaction_date.strftime(DATE_FORMAT),
        "amount": float(amount),
        "category": category,
        "description": description.strip() or "No description",
    }])

    row.to_csv(DATA_FILE, mode="a", header=False, index=False)


def load_budgets():
    if not BUDGET_FILE.exists():
        return {}

    try:
        with BUDGET_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_budgets(budgets):
    with BUDGET_FILE.open("w", encoding="utf-8") as file:
        json.dump(budgets, file, indent=2)


def money(value):
    return f"{CURRENCY}{value:,.2f}"


def month_transactions(df, selected_month):
    return df[
        (df["date"].dt.year == selected_month.year)
        & (df["date"].dt.month == selected_month.month)
    ].copy()


def totals(df):
    income = df.loc[df["category"] == "Income", "amount"].sum()
    expenses = df.loc[df["category"] == "Expense", "amount"].sum()
    return float(income), float(expenses), float(income - expenses)


def flash(message):
    """Queue a message that survives st.rerun()."""
    st.session_state["flash_message"] = message


def show_flash():
    message = st.session_state.pop("flash_message", None)
    if message:
        st.toast(message, icon="✅")


def month_picker(label, df, key):
    """Dropdown of months that have data, plus the current month."""
    months = {pd.Period(default_month, "M")}

    if not df.empty:
        months.update(df["date"].dt.to_period("M").unique())

    options = sorted(months, reverse=True)

    chosen = st.selectbox(
        label,
        options,
        index=options.index(pd.Period(default_month, "M")),
        format_func=lambda p: p.strftime("%B %Y"),
        key=key,
    )

    return date(chosen.year, chosen.month, 1)


def metric_card(label, value, note, icon):
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{icon} &nbsp; {label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_transactions_table(df):
    if df.empty:
        st.info("No transactions match these filters.")
        return

    display = df.copy()
    display["date"] = display["date"].dt.strftime(DATE_FORMAT)
    display["amount"] = display["amount"].map(money)

    display = display.rename(columns={
        "date": "Date",
        "amount": "Amount",
        "category": "Type",
        "description": "Description",
    })

    st.dataframe(display, hide_index=True, **STRETCH)


# ---------------------------- Sidebar ----------------------------

st.sidebar.markdown("## 💰 My Finance")
st.sidebar.caption("Personal money dashboard")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add transaction", "Transactions", "Monthly budget"],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("Your data is stored locally in CSV and JSON files.")
st.sidebar.caption(f"Transaction file: `{DATA_FILE.name}`")
st.sidebar.divider()
st.sidebar.caption("Made with Python · Streamlit · Pandas · Plotly")


# ---------------------------- Load data ----------------------------

df = load_transactions()

today = date.today()
default_month = date(today.year, today.month, 1)

show_flash()

st.markdown(
    """
    <div class="hero">
      <h1>Personal Finance Dashboard</h1>
      <p>Understand your spending, track your income, and stay on top of your goals.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------- Dashboard ----------------------------

if page == "Dashboard":

    top_left, top_right = st.columns([2, 1])

    with top_left:
        st.markdown("### Your financial overview")

    with top_right:
        selected_month = month_picker("Choose month", df, key="dashboard_month")

    current = month_transactions(df, selected_month)
    income, expenses, balance = totals(current)
    savings_rate = (balance / income * 100) if income > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Income", money(income), "Money received this month", "↗")
    with c2:
        metric_card("Expenses", money(expenses), "Money spent this month", "↘")
    with c3:
        metric_card("Net savings", money(balance), "Income minus expenses", "◎")
    with c4:
        metric_card(
            "Savings rate",
            f"{savings_rate:.1f}%",
            "Net savings as a share of income",
            "％",
        )

    st.write("")

    left, right = st.columns([1.35, 1])

    # Income vs expenses chart
    with left:
        st.markdown(
            '<div class="section-title">Income vs expenses</div>',
            unsafe_allow_html=True,
        )

        if current.empty:
            st.info("Add transactions to see your monthly chart.")
        else:
            chart_data = pd.DataFrame({
                "Type": ["Income", "Expenses"],
                "Amount": [income, expenses],
            })

            fig = px.bar(
                chart_data,
                x="Type",
                y="Amount",
                color="Type",
                color_discrete_map={"Income": "#176448", "Expenses": "#E47B70"},
                text_auto=".2s",
            )

            fig.update_layout(
                showlegend=False,
                height=330,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis_title="Amount (₹)",
                xaxis_title="",
                font=dict(family="DM Sans", color="#18372D"),
                yaxis=dict(
                    title_font=dict(color="#176448"),
                    tickfont=dict(color="#52665A"),
                    gridcolor="#E3ECE6",
                ),
                xaxis=dict(tickfont=dict(color="#176448", size=13)),
            )

            st.plotly_chart(fig, **STRETCH)

    # Spending breakdown chart
    with right:
        st.markdown(
            '<div class="section-title">Spending breakdown</div>',
            unsafe_allow_html=True,
        )

        expense_data = current[current["category"] == "Expense"].copy()

        if expense_data.empty:
            st.info("Your expense breakdown will appear here.")
        else:
            # Normalise descriptions so "groceries" and "Groceries " merge.
            expense_data["label"] = (
                expense_data["description"]
                .str.strip()
                .str.title()
                .replace("", "No Description")
            )

            category_data = (
                expense_data
                .groupby("label", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )

            fig = px.pie(
                category_data,
                names="label",
                values="amount",
                hole=0.62,
                color_discrete_sequence=[
                    "#176448",
                    "#4c9b78",
                    "#91c5a9",
                    "#e5b76a",
                    "#d98275",
                ],
            )

            fig.update_layout(
                height=330,
                margin=dict(l=5, r=5, t=15, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                legend_title_text="",
            )

            st.plotly_chart(fig, **STRETCH)

    # Recent transactions (selected month)
    st.markdown(
        '<div class="section-title">Recent transactions this month</div>',
        unsafe_allow_html=True,
    )

    show_transactions_table(current.head(7))

    # Monthly budget progress
    budgets = load_budgets()
    budget_key = selected_month.strftime("%Y-%m")
    monthly_budget = float(budgets.get(budget_key, 0) or 0)

    if monthly_budget > 0:
        st.markdown(
            '<div class="section-title">Monthly budget progress</div>',
            unsafe_allow_html=True,
        )

        st.progress(min(expenses / monthly_budget, 1.0))

        st.caption(
            f"{money(expenses)} spent of {money(monthly_budget)} budget · "
            f"{money(max(monthly_budget - expenses, 0))} remaining"
        )

        if expenses > monthly_budget:
            st.warning("You have exceeded your monthly spending budget.")


# ---------------------------- Add transaction ----------------------------

elif page == "Add transaction":

    st.markdown("### Add a transaction")
    st.caption("Record money coming in or going out.")

    with st.form("add_transaction_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            transaction_date = st.date_input(
                "Transaction date",
                value=today,
                format="DD/MM/YYYY",
            )

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                value=100.00,
                step=50.00,
            )

        with col2:
            category = st.selectbox(
                "Transaction type",
                ["Expense", "Income"],
                key="transaction_type",
            )

            description = st.text_input(
                "Description",
                placeholder="e.g. Salary, Groceries, Travel",
            )

        submitted = st.form_submit_button(
            "Save transaction",
            type="primary",
            **STRETCH,
        )

    if submitted:
        append_transaction(transaction_date, amount, category, description)
        flash(f"Saved {category.lower()} of {money(amount)}.")
        st.rerun()


# ---------------------------- Transaction history ----------------------------

elif page == "Transactions":

    st.markdown("### Transaction history")
    st.caption("Search and filter the transactions saved in your finance CSV.")

    if df.empty:
        st.info("No transactions yet. Add your first transaction to get started.")

    else:
        f1, f2, f3 = st.columns([1, 1, 1.4])

        min_date = df["date"].min().date()
        max_date = df["date"].max().date()

        with f1:
            start = st.date_input(
                "From",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                format="DD/MM/YYYY",
            )

        with f2:
            end = st.date_input(
                "To",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                format="DD/MM/YYYY",
            )

        with f3:
            type_filter = st.selectbox("Type", ["All", "Income", "Expense"])

        search = st.text_input("Search description", placeholder="Type a keyword...")

        filtered = df.copy()

        if start > end:
            st.error("The start date must be on or before the end date.")
            filtered = filtered.iloc[0:0]
        else:
            filtered = filtered[
                (filtered["date"].dt.date >= start)
                & (filtered["date"].dt.date <= end)
            ]

        if type_filter != "All":
            filtered = filtered[filtered["category"] == type_filter]

        if search.strip():
            filtered = filtered[
                filtered["description"].str.contains(
                    search.strip(), case=False, na=False, regex=False
                )
            ]

        st.caption(f"{len(filtered)} transaction(s) found")

        show_transactions_table(filtered)

        if not filtered.empty:
            export = filtered.copy()
            export["date"] = export["date"].dt.strftime(DATE_FORMAT)

            csv_bytes = export[COLUMNS].to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download filtered CSV",
                data=csv_bytes,
                file_name="finance_transactions.csv",
                mime="text/csv",
            )


# ---------------------------- Monthly budget ----------------------------

elif page == "Monthly budget":

    st.markdown("### Monthly spending budget")
    st.caption("Set a monthly expense limit and monitor how much you have used.")

    budgets = load_budgets()

    budget_month = month_picker("Budget month", df, key="budget_month")
    budget_key = budget_month.strftime("%Y-%m")

    existing_budget = float(budgets.get(budget_key, 0) or 0)

    month_data = month_transactions(df, budget_month)
    _, month_expenses, _ = totals(month_data)

    col1, col2 = st.columns(2)

    with col1:
        new_budget = st.number_input(
            "Monthly expense budget (₹)",
            min_value=0.0,
            value=existing_budget,
            step=500.0,
            key=f"budget_input_{budget_key}",
        )

        if st.button("Save monthly budget", type="primary", **STRETCH):
            budgets[budget_key] = float(new_budget)
            save_budgets(budgets)
            flash("Monthly budget saved.")
            st.rerun()

    with col2:
        st.markdown("#### Budget summary")

        if existing_budget > 0:
            remaining = existing_budget - month_expenses
            used = month_expenses / existing_budget

            st.metric("Spent this month", money(month_expenses))
            st.metric("Budget remaining", money(remaining))
            st.progress(min(max(used, 0.0), 1.0))
            st.caption(f"{used * 100:.1f}% of your saved budget used")

            if remaining < 0:
                st.error(f"You are over budget by {money(abs(remaining))}.")
            elif used >= 0.8:
                st.warning("You have used at least 80% of your budget.")
            else:
                st.success("You are within your monthly budget.")
        else:
            st.info("Enter and save a budget to start tracking your spending.")

    st.markdown("---")
    st.markdown("#### Monthly expense history")

    expense_history = df[df["category"] == "Expense"].copy()

    if expense_history.empty:
        st.info("Your monthly expense trend will appear once you add expenses.")
    else:
        expense_history["month"] = expense_history["date"].dt.to_period("M").astype(str)

        monthly = (
            expense_history
            .groupby("month", as_index=False)["amount"]
            .sum()
            .sort_values("month")
        )

        fig = px.bar(
            monthly,
            x="month",
            y="amount",
            labels={"month": "Month", "amount": "Expenses (₹)"},
            color_discrete_sequence=["#176448"],
        )

        fig.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig, **STRETCH)
