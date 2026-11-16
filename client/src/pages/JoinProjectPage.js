import JoinProjectForm from "../components/JoinProjectForm";
import PageHeader from "../components/PageHeader";

// Stand-alone Join page. The dashboard's Join Project tab uses the same form.
function JoinProjectPage() {
  return (
    <section className="checkout-page">
      <PageHeader title="Join Project" />

      <div className="checkout-content">
        <JoinProjectForm />
      </div>
    </section>
  );
}

export default JoinProjectPage;
