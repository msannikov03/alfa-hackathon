export const getClientUserId = (): number => {
  if (typeof window === "undefined") {
    return 1;
  }

  const stored = window.localStorage.getItem("user_id");
  const parsed = stored ? parseInt(stored, 10) : NaN;

  return Number.isFinite(parsed) ? parsed : 1;
};
