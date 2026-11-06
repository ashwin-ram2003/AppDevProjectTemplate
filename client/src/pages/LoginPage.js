import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function LoginPage() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!userId || !password) {
      setMessage("Please enter your User ID and password.");
      return;
    }

    try {
      const response = await fetch("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: userId,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.error || "Unable to sign in.");
        return;
      }

      navigate("/dashboard");
    } catch (error) {
      setMessage("Unable to connect to the server.");
    }
  };

  return (
    <section className="account-page">
      <div className="account-card">
        <h1>Sign In</h1>

        <form onSubmit={handleSubmit}>
          <label htmlFor="user-id">User ID</label>
          <input
            id="user-id"
            type="text"
            value={userId}
            onChange={(event) => setUserId(event.target.value)}
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />

          <button
            className="button button-primary account-button"
            type="submit"
          >
            Sign In
          </button>

          {message && <p className="account-message">{message}</p>}
        </form>

        <Link to="/create-account">Create Account</Link>
      </div>
    </section>
  );
}

export default LoginPage;