const aiProvider = document.getElementById("ai_provider");
const aiModel = document.getElementById("ai_model");
const aiModelUpdateError = document.getElementById("ai-model-update-error");
let latestModelRequest = 0;

aiProvider.onchange = async () => {
    await updateAiModels();
};

export async function updateAiModels() {
  const requestId = ++latestModelRequest;
  const url = new URL(aiProvider.dataset.modelsUrl, window.location.origin);
  url.searchParams.set("ai_provider", aiProvider.value);
  aiModelUpdateError.hidden = true;
  aiModelUpdateError.textContent = "";

  try {
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`Unable to load AI models (${response.status})`);
    }

    const models = await response.json();
    console.log(models)
    if (
        !Array.isArray(models) ||
        !models.every(model =>
          model !== null &&
          typeof model.name === "string" &&
          typeof model.model === "string"
        )
      ) {
      throw new Error("Expected a list of AI model options as strings");
    }

    if (requestId === latestModelRequest) {
      aiModel.replaceChildren(...models.map(model =>
        new Option(model.name, model.model, false, model.model === aiModel.dataset.selectedModel)
      ));
    }
    aiModel.disabled = false;
  } catch (error) {
    if (requestId === latestModelRequest) {
      aiModelUpdateError.textContent = "Could not update AI models. Check the AI URL and try again.";
      aiModelUpdateError.hidden = false;
      console.error("Could not update AI models:", error);
    }
  }
}

updateAiModels().then(r => {}).catch(error => {
  aiModelUpdateError.textContent = "Could not update AI models. Check the AI URL and try again.";
  aiModelUpdateError.hidden = false;
  console.error("Could not update AI models:", error);
});
