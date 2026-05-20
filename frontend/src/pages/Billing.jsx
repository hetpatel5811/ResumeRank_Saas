import { useCallback, useEffect, useState } from "react";
import { ArrowRight, CheckCircle2, CircleAlert, Crown, Sparkles } from "lucide-react";
import Navbar from "../components/Navbar";
import api from "../api/api";

const PENDING_SUBSCRIPTION_STORAGE_KEY = "resume_rank_pending_subscription_id";
const PAYMENTS_ENABLED = false;

function Billing() {
  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState("free");
  const [pendingSubscriptionId, setPendingSubscriptionId] = useState(
    () => localStorage.getItem(PENDING_SUBSCRIPTION_STORAGE_KEY) || ""
  );
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [processingPlan, setProcessingPlan] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState(
    PAYMENTS_ENABLED
      ? ""
      : "Payments coming soon. Razorpay onboarding and approval are in progress."
  );

  const loadBillingData = useCallback(async () => {
    try {
      const [userRes, plansRes] = await Promise.all([
        api.get("/api/auth/me"),
        api.get("/api/billing/plans"),
      ]);

      setCurrentPlan((userRes.data?.plan || "free").toLowerCase());
      setPlans(plansRes.data?.plans || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load plan data.");
    } finally {
      setLoading(false);
    }
  }, []);

  const verifySubscriptionStatus = useCallback(async (subscriptionId) => {
    if (!subscriptionId) {
      setError("No pending subscription found. Start an upgrade first.");
      return;
    }

    setVerifying(true);
    setError("");

    try {
      const res = await api.get(`/api/billing/subscriptions/${subscriptionId}`);
      const subscriptionStatus = (res.data?.status || "").toLowerCase();
      const paymentState = (res.data?.payment_state || "").toLowerCase();
      const planApplied = (res.data?.plan_applied || "free").toLowerCase();

      setCurrentPlan(planApplied);

      if (paymentState === "paid" && ["authenticated", "active"].includes(subscriptionStatus)) {
        setMessage(`Payment confirmed. Your plan is now ${planApplied.toUpperCase()}.`);
        localStorage.removeItem(PENDING_SUBSCRIPTION_STORAGE_KEY);
        setPendingSubscriptionId("");
        await loadBillingData();
      } else {
        if (["cancelled", "completed", "expired"].includes(subscriptionStatus)) {
          setMessage(`Subscription is ${subscriptionStatus}. You can start a new upgrade anytime.`);
          localStorage.removeItem(PENDING_SUBSCRIPTION_STORAGE_KEY);
          setPendingSubscriptionId("");
        } else {
          setMessage(
            `Subscription status: ${subscriptionStatus || "created"}. If you completed payment, verify again in a few seconds.`
          );
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Could not verify subscription yet.");
    } finally {
      setVerifying(false);
    }
  }, [loadBillingData]);

  const startSubscription = async (planId) => {
    if (!PAYMENTS_ENABLED) {
      setError("");
      setMessage("Payments coming soon. Razorpay onboarding and approval are in progress.");
      return;
    }

    setProcessingPlan(planId);
    setError("");
    setMessage("");

    try {
      const res = await api.post("/api/billing/subscriptions", {
        plan: planId,
      });

      const subscriptionId = res.data?.subscription_id;
      const authUrl = res.data?.auth_url;

      if (!subscriptionId || !authUrl) {
        setError("Could not start Razorpay subscription. Missing checkout details.");
        setProcessingPlan("");
        return;
      }

      localStorage.setItem(PENDING_SUBSCRIPTION_STORAGE_KEY, subscriptionId);
      setPendingSubscriptionId(subscriptionId);
      window.open(authUrl, "_blank", "noopener,noreferrer");
      setMessage("Razorpay page opened in a new tab. Complete payment there and then verify here.");
      setProcessingPlan("");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to start Razorpay subscription.");
      setProcessingPlan("");
    }
  };

  useEffect(() => {
    if (!PAYMENTS_ENABLED) {
      localStorage.removeItem(PENDING_SUBSCRIPTION_STORAGE_KEY);
      setPendingSubscriptionId("");
    }

    const timer = window.setTimeout(() => {
      loadBillingData();
    }, 0);

    return () => window.clearTimeout(timer);
  }, [loadBillingData]);

  const currentPlanLabel = currentPlan.toUpperCase();

  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-content">
        <div className="page-heading">
          <span className="eyebrow">Subscriptions</span>
          <h1>Upgrade your scanning capacity</h1>
          <p>Choose a plan and complete checkout securely through Razorpay.</p>
        </div>

        <section className="billing-current-plan">
          <div>
            <p className="plan-kicker">Current Plan</p>
            <h2>{currentPlanLabel}</h2>
          </div>
          <div className="plan-chip">
            <Sparkles size={16} />
            {currentPlan === "free" ? "Upgrade for more scans" : "Paid plan active"}
          </div>
        </section>

        {(loading || verifying) && (
          <div className="loading-box">
            {loading ? "Loading subscription options..." : "Verifying payment..."}
          </div>
        )}

        {error && (
          <div className="error-box">
            <CircleAlert size={18} />
            <span>{error}</span>
          </div>
        )}

        {message && (
          <div className="billing-message">
            <CheckCircle2 size={18} />
            <span>{message}</span>
          </div>
        )}

        {pendingSubscriptionId && (
          <section className="billing-pending-card">
            <p>
              Pending Subscription: <strong>{pendingSubscriptionId}</strong>
            </p>
            <div className="billing-actions-row">
              <button
                className="secondary-link"
                type="button"
                onClick={() => verifySubscriptionStatus(pendingSubscriptionId)}
                disabled={verifying || !PAYMENTS_ENABLED}
              >
                {verifying ? "Verifying..." : "I completed payment, verify now"}
              </button>
            </div>
          </section>
        )}

        {!loading && (
          <section className="billing-grid">
            {plans.map((plan) => {
              const isCurrent = currentPlan === plan.id || plan.is_current;
              const isBusy = processingPlan === plan.id;
              const canPurchase = plan.can_purchase;

              return (
                <article key={plan.id} className={`billing-card ${isCurrent ? "current" : ""}`}>
                  <div className="billing-card-head">
                    <div className="billing-title-row">
                      <h2>{plan.name}</h2>
                      <Crown size={18} />
                    </div>
                    <p>{plan.description}</p>
                    <h3>{plan.price_label}</h3>
                  </div>

                  <ul>
                    {plan.features.map((feature) => (
                      <li key={feature}>
                        <CheckCircle2 size={16} />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {isCurrent ? (
                    <button className="secondary-link current-btn" disabled>
                      Current Plan
                    </button>
                  ) : !canPurchase ? (
                    <button className="secondary-link current-btn" disabled>
                      Not Available
                    </button>
                  ) : (
                    <button
                      className="primary-btn upgrade-btn"
                      onClick={() => startSubscription(plan.id)}
                      disabled={isBusy}
                    >
                      {isBusy ? "Starting..." : `Upgrade to ${plan.name}`}
                      <ArrowRight size={18} />
                    </button>
                  )}
                </article>
              );
            })}
          </section>
        )}
      </main>
    </div>
  );
}

export default Billing;
