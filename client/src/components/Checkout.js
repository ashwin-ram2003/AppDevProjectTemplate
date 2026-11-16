import { useEffect, useState } from "react";

import { fetchHardwareDetail, fetchHardwareSets } from "../api/hardwareApi";
import CheckoutForm from "./CheckoutForm";
import CurrentHardware from "./CurrentHardware";
import HardwareTable from "./HardwareTable";
import PageHeader from "./PageHeader";

function Checkout() {
  const [hardware, setHardware] = useState([]);
  const [selectedHardware, setSelectedHardware] = useState(null);
  const [expandedName, setExpandedName] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    fetchHardwareSets()
      .then((items) => {
        if (!active) return;
        setHardware(items);
        setSelectedHardware(items[0] || null);
      })
      .catch((requestError) => active && setError(requestError.message))
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, []);

  const toggleDetail = async (item) => {
    if (expandedName === item.name) {
      setExpandedName(null);
      setDetail(null);
      return;
    }

    setExpandedName(item.name);
    setDetail(null);
    setDetailLoading(true);
    try {
      const fullHardware = await fetchHardwareDetail(item.name);
      setDetail(fullHardware);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <section className="checkout-page">
      <PageHeader title="Hardware Checkout" />
      <div className="checkout-content">
        <section aria-label="Hardware inventory">
          {loading && <p className="loading-message">Loading hardware inventory…</p>}
          {error && <p className="error-banner" role="alert">{error}</p>}
          {!loading && !error && hardware.length === 0 && (
            <p className="empty-state">No hardware sets are currently configured.</p>
          )}
          {hardware.length > 0 && (
            <HardwareTable
              hardware={hardware}
              expandedName={expandedName}
              detail={detail}
              detailLoading={detailLoading}
              onRequest={setSelectedHardware}
              onToggleDetail={toggleDetail}
            />
          )}
        </section>

        <div className="action-grid">
          <CheckoutForm hardware={selectedHardware} />
          <CurrentHardware />
        </div>
      </div>
    </section>
  );
}

export default Checkout;
