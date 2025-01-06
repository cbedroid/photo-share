$(document).ready(function () {
    const policyAction = document.getElementById("privacy_policy");
    const policyButtons = policyAction.querySelectorAll("button[role='tab']");
    if (!policyButtonArray) return;

    // Attach click listener to each policy action buttons.
    const policyButtonArray = Array.from(policyButtons);
    policyButtonArray.forEach((button) => {
        button.addEventListener(("click"), function () {
            const tabName = this.getAttribute("data-bs-target");
            if (tabName) {
                const tabElement = document.getElementById(tabName)
                tabElement.scrollIntoView({behavior: "smooth"})
                // Remove the `active` class from each button
                policyButtonArray.forEach((el) => el.classList.remove("active"));
                // Add active class to the current button
                this.classList.add("active");
            }
        })
    })
})
