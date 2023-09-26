console.log('Button clicked');
// ...rest of your code

document.addEventListener('DOMContentLoaded', function() {
    const recommendBtn = document.getElementById('recommend-btn');
    const skillsInput = document.getElementById('skills');
    const recommendationsDiv = document.getElementById('recommendations');

    recommendBtn.addEventListener('click', async function() {
        const inputSkills = skillsInput.value.split(',').map(skill => skill.trim());

        const requestBody = {
            skills: inputSkills,
            num_recommendations: 5 // Adjust as needed
        };

        try {
            const response = await fetch('/get_recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            console.log(data); // Log the response data to the console
            populateRecommendations(data);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
        }

    });

    function populateRecommendations(recommendations) {
        let html = '<h2>Recommendations:</h2>';
        for (const recommendation of recommendations) {
            html += `<div><strong>Domain:</strong> ${recommendation.Domain}</div>`;
            html += '<ul>';
            html += '<strong>Future Skills:</strong>';
            for (const skill of recommendation['Future Skills']) {
                html += `<li>${skill}</li>`;
            }
            html += '</ul>';
        }

        recommendationsDiv.innerHTML = html;
    }
});
console.log('Button clicked');
// Function to load and display emerging skills
function loadEmergingSkills() {
    // Make an AJAX request to your server to fetch emerging skills
    // Update the 'emergingSkillsContent' container with the fetched content
    // For example:
    fetch('/get_emerging_skills')
        .then(response => response.json())
        .then(data => {
            const emergingSkillsContent = document.getElementById('emergingSkillsContent');
            // Populate 'emergingSkillsContent' with the fetched skills
            // You can format and display the skills as needed
            emergingSkillsContent.innerHTML = data.skills.join('<br>');
        })
        .catch(error => console.error('Error fetching emerging skills:', error));
}

// Add event listener for "Emerging Skills" link
document.querySelector('#emergingSkillsCard').addEventListener('click', loadEmergingSkills);

function loadEmergingJobs() {
    // Make an AJAX request to your server to fetch emerging skills
    // Update the 'emergingSkillsContent' container with the fetched content
    // For example:
    fetch('/get_emerging_jobs')
        .then(response => response.json())
        .then(data => {
            const emergingSkillsContent = document.getElementById('emergingjobsContent');
            // Populate 'emergingSkillsContent' with the fetched skills
            // You can format and display the skills as needed
            emergingjobsContent.innerHTML = data.skills.join('<br>');
        })
        .catch(error => console.error('Error fetching emerging skills:', error));
}

// Add event listener for "Emerging Skills" link
document.querySelector('#emergingjobsCard').addEventListener('click', loadEmergingJobs);



const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null; // Variable to store user's message
const API_KEY = "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"; // Paste your API key here
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi; // return chat <li> element
}

const generateResponse = (chatElement) => {
    const API_URL = "https://api.openai.com/v1/chat/completions";
    const messageElement = chatElement.querySelector("p");

    // Define the properties and message for the API request
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${API_KEY}`
        },
        body: JSON.stringify({
            model: "gpt-3.5-turbo",
            messages: [{ role: "user", content: userMessage }],
        })
    }

    // Send POST request to API, get response and set the reponse as paragraph text
    fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
        messageElement.textContent = data.choices[0].message.content.trim();
    }).catch(() => {
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
    }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
}

const handleChat = () => {
    userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
    if (!userMessage) return;

    // Clear the input textarea and set its height to default
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);

    setTimeout(() => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
}

chatInput.addEventListener("input", () => {
    // Adjust the height of the input textarea based on its content
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window 
    // width is greater than 800px, handle the chat
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));