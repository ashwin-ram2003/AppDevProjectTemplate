import { useState } from "react";
import { Link } from "react-router-dom";

function CreateAccountPage() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!userId || !password || !confirmPassword) {
      setMessage("Please fill out all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }

    try {
      const response = await fetch("/add_user", {
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
      setMessage(data.error || "Unable to create account.");
      return;
    }

    setMessage("Account created successfully.");
  } catch (error) {
    setMessage("Unable to connect to the server.");
}
  };

  return (
    <section className="account-page">
      <div className="account-card">
        <h1>Create Account</h1>

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

          <label htmlFor="confirm-password">Confirm Password</label>
          <input
            id="confirm-password"
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
          />

          <button className="button button-primary account-button" type="submit">
            Create Account
          </button>

          {message && <p className="account-message">{message}</p>}
        </form>

        <Link to="/">Back to Sign In</Link>
      </div>
    </section>
  );
}

export default CreateAccountPage;