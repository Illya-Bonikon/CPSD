// Секції
const sections = {
    add: document.getElementById("addMeterSection"),
    update: document.getElementById("updateMeterSection"),
    history: document.getElementById("historyMeterSection")
};

// Кнопки навігації
document.getElementById("addMeterBtn").addEventListener("click", () => showSection("add"));
document.getElementById("updateMeterBtn").addEventListener("click", () => showSection("update"));
document.getElementById("historyMeterBtn").addEventListener("click", () => showSection("history"));

function showSection(name) {
    Object.values(sections).forEach(sec => sec.style.display = "none");
    sections[name].style.display = "block";
}

// Валідація інпутів
function validateInput(inputId, validationFn) {
    const input = document.getElementById(inputId);
    const isValid = validationFn(input.value);
    input.style.borderColor = isValid ? "#ccc" : "red";
    return isValid;
}

function isValidId(value) {
    return /^[a-zA-Z0-9]+$/.test(value);
}

function isPositiveNumber(value) {
    const num = parseFloat(value);
    return !isNaN(num) && num > 0;
}

// ======= Додавання лічильника =======
const addForm = document.getElementById("addMeterForm");
const addSubmit = document.getElementById("submitAdd");
const addMessage = document.getElementById("addMeterMessage");

addForm.addEventListener("input", () => {
    const valid =
        validateInput("meterId", isValidId) &&
        validateInput("dayValue", isPositiveNumber) &&
        validateInput("nightValue", isPositiveNumber);

    addSubmit.disabled = !valid;
});

addForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        meterId: document.getElementById("meterId").value,
        dayReading: +document.getElementById("dayValue").value,
        nightReading: +document.getElementById("nightValue").value
    };

    try {
        const res = await fetch("/api/meters/new", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (res.ok) {
            addMessage.textContent = `✅ Лічильник додано! Сума: ${result.totalAmount} грн.`;
            addMessage.style.color = "green";
            await loadMeterIds(); // оновлюємо автозаповнення
        } else {
            throw new Error(result.error || "Помилка");
        }
    } catch (err) {
        console.error(err);
        addMessage.textContent = "❌ Помилка при додаванні.";
        addMessage.style.color = "red";
    }
});

// ======= Оновлення лічильника =======
const updateForm = document.getElementById("updateMeterForm");
const updateSubmit = document.getElementById("submitUpdate");
const updateMessage = document.getElementById("updateMeterMessage");

updateForm.addEventListener("input", () => {
    const valid =
        validateInput("updateMeterId", isValidId) &&
        validateInput("updateDayValue", isPositiveNumber) &&
        validateInput("updateNightValue", isPositiveNumber);

    updateSubmit.disabled = !valid;
});

updateForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const meterId = document.getElementById("updateMeterId").value;
    const data = {
        meterId,
        newDayReading: +document.getElementById("updateDayValue").value,
        newNightReading: +document.getElementById("updateNightValue").value
    };

    try {
        const res = await fetch(`/api/meters/update`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (res.ok) {
            updateMessage.textContent = `✅ Оновлено. Сума: ${result.totalAmount} грн.`;
            updateMessage.style.color = "green";
        } else {
            throw new Error(result.error || "Помилка");
        }
    } catch (err) {
        console.error(err);
        updateMessage.textContent = "❌ Помилка при оновленні.";
        updateMessage.style.color = "red";
    }
});

// ======= Пошук історії =======
const historyForm = document.getElementById("historyForm");
historyForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const meterId = document.getElementById("historyMeterId").value;

    try {
        const res = await fetch(`/api/meters/${meterId}/history`);
        const data = await res.json();

        if (res.ok) {
            renderHistoryTable(data);
        } else {
            throw new Error(data.error || "Помилка");
        }
    } catch (err) {
        console.error(err);
        document.getElementById("historyTable").textContent = "❌ Помилка при отриманні історії.";
    }
});

function renderHistoryTable(data) {
    const table = document.createElement("table");
    const header = table.insertRow();
    ["Дата", "День", "Ніч", "Сума"].forEach(text => {
        const cell = header.insertCell();
        cell.textContent = text;
    });

    data.forEach(entry => {
        const row = table.insertRow();
        row.insertCell().textContent = new Date(entry.date).toLocaleString();
        row.insertCell().textContent = entry.currentDayReading;
        row.insertCell().textContent = entry.currentNightReading;
        row.insertCell().textContent = entry.totalAmount.toFixed(2);
    });

    const container = document.getElementById("historyTable");
    container.innerHTML = "";
    container.appendChild(table);
}

// ======= Автозаповнення ID =======
async function loadMeterIds() {
    try {
        const res = await fetch("/api/meters");
        const data = await res.json();

        if (!Array.isArray(data)) throw new Error("Невірний формат");

        const datalist = document.getElementById("meterIdList");
        datalist.innerHTML = "";
        data.forEach(meter => {
            const opt = document.createElement("option");
            opt.value = meter.meterId;
            datalist.appendChild(opt);
        });
    } catch (err) {
        console.error("Помилка автозаповнення ID:", err);
    }
}

// Запускаємо при завантаженні
loadMeterIds();
