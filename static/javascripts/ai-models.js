const aiProvider = document.getElementById("ai_provider");
const aiModel = document.getElementById("ai_model");
const aiModelUpdateError = document.getElementById("ai-model-update-error");
const embeddingModel = document.getElementById("embedding_model");
const embeddingModelUpdateError = document.getElementById("embedding-model-update-error");
let latestModelRequest = 0;
let latestEmbeddingModelRequest = 0;

aiProvider.onchange = () => {
    aiModel.dataset.selectedModel = "";
    embeddingModel.dataset.selectedModel = "";
    updateAiModels();
    updateEmbeddingModels();
};

export async function updateAiModels() {
  const requestId = ++latestModelRequest;
  const url = new URL(aiProvider.dataset.modelsUrl, window.location.origin);
  url.searchParams.set("ai_provider", aiProvider.value);
  aiModel.disabled = true;
  aiModel.replaceChildren();
  aiModelUpdateError.hidden = true;
  aiModelUpdateError.textContent = "";

  try {
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`Unable to load AI models (${response.status})`);
    }

    const models = await response.json();
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
      aiModel.disabled = false;
    }
  } catch (error) {
    if (requestId === latestModelRequest) {
      aiModelUpdateError.textContent = "Could not update AI models. Check the AI URL and try again.";
      aiModelUpdateError.hidden = false;
      console.error("Could not update AI models:", error);
    }
  }
}

export async function updateEmbeddingModels() {
  const requestId = ++latestEmbeddingModelRequest;
  const url = new URL(aiProvider.dataset.embeddingModelsUrl, window.location.origin);
  url.searchParams.set("ai_provider", aiProvider.value);
  embeddingModel.disabled = true;
  embeddingModel.replaceChildren();
  embeddingModelUpdateError.hidden = true;
  embeddingModelUpdateError.textContent = "";

  try {
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`Unable to load embedding models (${response.status})`);
    }

    const models = await response.json();
    if (!Array.isArray(models) || !models.length || !models.every(model => typeof model === "string" && model)) {
      throw new Error("Expected a non-empty list of embedding model names");
    }

    if (requestId === latestEmbeddingModelRequest) {
      embeddingModel.replaceChildren(...models.map(model =>
        new Option(model, model, false, model === embeddingModel.dataset.selectedModel)
      ));
      embeddingModel.disabled = false;
    }
  } catch (error) {
    if (requestId === latestEmbeddingModelRequest) {
      embeddingModelUpdateError.textContent = "Could not update embedding models. Try again.";
      embeddingModelUpdateError.hidden = false;
      console.error("Could not update embedding models:", error);
    }
  }
}

updateAiModels();
updateEmbeddingModels();
