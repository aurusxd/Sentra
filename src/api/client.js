import axios from "axios";

const api = axios.create({
    baseURL: "https://api.sentra.fun",
    withCredentials: true,
});

export default api;
