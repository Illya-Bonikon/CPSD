// Секції
const sections = {
    add: document.getElementById("addMeterSection"),
    update: document.getElementById("updateMeterSection"),
    history: document.getElementById("historyMeterSection")
};

// Показуємо секцію
function showSection(name) {
    Object.values(sections).forEach(sec => sec.style.display = "none");
    sections[name].style.display = "block";
}

// Кнопки навігації
document.getElementById("addMeterBtn").addEventListener("click", () => showSection("add"));
document.getElementById("updateMeterBtn").addEventListener("click", () => showSection("update"));
document.getElementById("historyMeterBtn").addEventListener("click", () => showSection("history"));

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

// Перевірка, чи лічильник з таким ID вже існує
let existingMeterIds = []; // Список існуючих ID

async function checkMeterIdExists(meterId) {
    try {
        // Оновлюємо список ID, якщо він порожній
        if (existingMeterIds.length === 0) 	await loadMeterIds(true);
        return existingMeterIds.includes(meterId);

    } catch (error) {
        console.error("Помилка перевірки ID:", error);
        return false;
    }
}



//			 Додавання лічильника


// Структура сторінки
const addForm = document.getElementById("addMeterForm");
const addSubmit = document.getElementById("submitAdd");
const addMessage = document.getElementById("addMeterMessage");
const meterIdInput = document.getElementById("meterId");

// Перевіряємо унікальність ID під час вводу
meterIdInput.addEventListener("input", async () => {
    if (isValidId(meterIdInput.value)) {
        const exists = await checkMeterIdExists(meterIdInput.value);
        if (exists) {
            addMessage.textContent = "❗ Лічильник з таким ID вже існує. Ви можете оновити його показники або подивитись історію.";
            addMessage.style.color = "orange";
            addSubmit.disabled = true;
            return;
        } else {
            addMessage.textContent = "";
        }
    }
    // Перевіряємо всі поля форми
    const valid =
        validateInput("meterId", isValidId) &&
        validateInput("dayValue", isPositiveNumber) &&
        validateInput("nightValue", isPositiveNumber);
	
	// Кнопка активна, якщо всі поля валідні
    addSubmit.disabled = !valid;
});

// Перевіряємо цифрові поля окремо
addForm.addEventListener("input", (e) => {
    if (e.target.id === "dayValue" || e.target.id === "nightValue") {
        const valid =
            validateInput("meterId", isValidId) &&
            validateInput("dayValue", isPositiveNumber) &&
            validateInput("nightValue", isPositiveNumber);

        // Перевіряємо чи ID вже існує
		addSubmit.disabled = !valid || existingMeterIds.includes(meterIdInput.value);
    }
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
            await loadMeterIds(true); 
            addForm.reset();
        } else {
            throw new Error(result.error || "Помилка");
        }
    } catch (err) {
        console.error(err);
        addMessage.textContent = "❌ Помилка при додаванні.";
        addMessage.style.color = "red";
    }
});



//					 Оновлення лічильника 



// Структура сторінки
const updateForm = document.getElementById("updateMeterForm");
const updateSubmit = document.getElementById("submitUpdate");
const updateMessage = document.getElementById("updateMeterMessage");
const updateMeterIdInput = document.getElementById("updateMeterId");

// Перевіряємо, чи існує лічильник для оновлення
updateMeterIdInput.addEventListener("input", async () => {
    if (isValidId(updateMeterIdInput.value)) {
        const exists = await checkMeterIdExists(updateMeterIdInput.value);
        if (!exists) {
            updateMessage.textContent = "❗ Лічильник з таким ID не знайдено. Перевірте ID або додайте новий лічильник.";
            updateMessage.style.color = "red";
            updateSubmit.disabled = true;
        } else {
            updateMessage.textContent = "";
            
            // Перевіряємо всі поля форми
            const valid =
                validateInput("updateMeterId", isValidId) &&
                validateInput("updateDayValue", isPositiveNumber) &&
                validateInput("updateNightValue", isPositiveNumber);
                
            updateSubmit.disabled = !valid;
        }
    }
});

updateForm.addEventListener("input", (e) => {
    if (e.target.id === "updateDayValue" || e.target.id === "updateNightValue") {
        const valid =
            validateInput("updateMeterId", isValidId) &&
            validateInput("updateDayValue", isPositiveNumber) &&
            validateInput("updateNightValue", isPositiveNumber);
            
        // Якщо ID не доданий до бд - форма залишається неактивною
		updateSubmit.disabled = !valid || !existingMeterIds.includes(updateMeterIdInput.value);
    }
});

updateForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const meterId = document.getElementById("updateMeterId").value.trim();
    const newDayReading = parseFloat(document.getElementById("updateDayValue").value);
    const newNightReading = parseFloat(document.getElementById("updateNightValue").value);

    if (isNaN(newDayReading) || isNaN(newNightReading)) {
        alert("❌ Некоректні значення. Введіть правильні числові дані.");
        return;
    }

    try {
        // Отримуємо останні показники для порівняння
        const latestRes = await fetch(`/api/meters/${meterId}/latest`);
        const latestData = await latestRes.json();
	
        if (!latestRes.ok || !latestData || latestData.currentDayReading === undefined)
            throw new Error("Не вдалося отримати попередні дані.");

        let adjustedDay = newDayReading;
        let adjustedNight = newNightReading;

        const dayDelta = newDayReading - latestData.currentDayReading;
        const nightDelta = newNightReading - latestData.currentNightReading;

        if (dayDelta < 0 || nightDelta < 0) {
            const confirmResult = confirm("⚠️ Нові показники менші за попередні. Це викличе накрутку. Продовжити?");
            if (!confirmResult) {
                updateMessage.textContent = "⛔ Дані не оновлено. Перевірте введені значення.";
                updateMessage.style.color = "orange";
                return;
            } 
        }

        const data = {
            meterId,
            newDayReading: adjustedDay,
            newNightReading: adjustedNight
        };

        const res = await fetch(`/api/meters/add-data`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (res.ok) {
            updateMessage.textContent = `✅ Оновлено. Сума: ${result.totalAmount} грн.`;
            updateMessage.style.color = "green";
            updateForm.reset(); 
        } else {
            throw new Error(result.error || "Помилка");
        }
    } catch (err) {
        console.error(err);
        updateMessage.textContent = "❌ Помилка при оновленні. " + (err.message || "");
        updateMessage.style.color = "red";
    }
});



// 				 Пошук історії 



// Структура сторінки
const historyForm = document.getElementById("historyForm");
const historyMessage = document.getElementById("historyTable");
const historyMeterIdInput = document.getElementById("historyMeterId");

historyMeterIdInput.addEventListener("input", async () => {
    if (isValidId(historyMeterIdInput.value)) {
        const exists = await checkMeterIdExists(historyMeterIdInput.value);
        if (!exists) {
            historyMessage.textContent = "❗ Лічильник з таким ID не знайдено.";
            historyMessage.style.color = "red";
            document.getElementById("submitHistory").disabled = true;
        } else {
            historyMessage.textContent = "";
            document.getElementById("submitHistory").disabled = false;
        }
    } else {
        document.getElementById("submitHistory").disabled = true;
    }
});

historyForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const meterId = document.getElementById("historyMeterId").value;

    try {
        const res = await fetch(`/api/meters/${meterId}/history`);
        const data = await res.json();

        if (res.ok)
            renderHistoryTable(data);
        else
            throw new Error(data.error || "Помилка");

    } catch (err) {
        console.error(err);
        historyMessage.textContent = "❌ Помилка при отриманні історії.";
    }
});

function formatDate(dateString) {
    const date = new Date(dateString);
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0'); // +1 бо місяці починаються з 0
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${day}.${month}.${year} ${hours}:${minutes}`;
}


function renderHistoryTable(data) {
    const table = document.createElement("table");
    const header = table.insertRow();
    ["Дата", "Показник день", "Показник ніч", "Порахований рахунок"].forEach(text => {
        const cell = header.insertCell();
        cell.textContent = text;
    });

    data.forEach(entry => {
        const row = table.insertRow();
        row.insertCell().textContent = formatDate(entry.date);
        row.insertCell().textContent = entry.currentDayReading;
        row.insertCell().textContent = entry.currentNightReading;
        row.insertCell().textContent = entry.totalAmount.toFixed(2) + " грн";
    });

    historyMessage.innerHTML = "";
    historyMessage.appendChild(table);
}


//  			Тулзи



// Автозаповнення ID 
async function loadMeterIds(updateCache = false) {
    try {
        const res = await fetch("/api/meters/ids");
        const data = await res.json();

        if (!Array.isArray(data))	 throw new Error("Невірний формат");

		if (updateCache) 	existingMeterIds = data;

        const datalists = document.querySelectorAll("#meterIdList");
        datalists.forEach(datalist => {
            datalist.innerHTML = "";
            data.forEach(meterId => {
                const opt = document.createElement("option");
                opt.value = meterId;
                datalist.appendChild(opt);
            });
        });
        
        return data;
    } catch (err) {
        console.error("Помилка автозаповнення ID:", err);
        return [];
    }
}

window.addEventListener("DOMContentLoaded", async () => {
    showSection("add");
    await loadMeterIds(true);
});