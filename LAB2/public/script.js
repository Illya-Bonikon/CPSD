document.getElementById("meterForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.target;
    const meterId = form.meterId.value;
    const dayValue = parseInt(form.dayValue.value, 10);
    const nightValue = parseInt(form.nightValue.value, 10);
    try {
        const response = await fetch("http://localhost:5000/api/meters/update", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                meterId: meterId,
                newDayReading: dayValue,
                newNightReading: nightValue
            })
        });
        if (response.ok) {
            const result = await response.json();
            document.getElementById("response").innerHTML = `The bill has been updated for the meter ${result.meterId}. Sum: ${result.totalAmount} hrn.`;
        } else {
            throw new Error("Error updating data.");
        }
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("response").innerHTML = "The data could not be updated. Please try again.";
    }
});
