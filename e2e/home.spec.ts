import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.route('**/update_ai_models?*', async route => {
    await route.fulfill({
      json: [{ name: 'Test model', model: 'test-model' }],
    });
  });

  await page.goto('/');
});

test('renders the service introduction', async ({ page }) => {
  await expect(page).toHaveTitle('Test Ontology Library - GOV.UK');
  await expect(
    page.getByRole('heading', { name: 'Test Ontology Library', level: 1 }),
  ).toBeVisible();
  await expect(
    page.getByText('Use this service to test Ontology generation using a variety of AI models and processing libraries.'),
  ).toBeVisible();
  await expect(page.getByText('This is a prototype service.')).toBeVisible();
});

test('renders empty run details and the submit buttons', async ({ page }) => {
  const runName = page.getByRole('textbox', { name: 'Run name', exact: true });
  await expect(runName).toBeVisible();
  await expect(runName).toBeEditable();
  await expect(runName).toBeEmpty();

  const processingPrompt = page.getByRole('textbox', { name: 'Processing Prompt', exact: true });
  await expect(processingPrompt).toBeVisible();
  await expect(processingPrompt).toBeEditable();
  await expect(processingPrompt).toBeEmpty();

  for (const name of ['Update', 'Start']) {
    await expect(page.getByRole('button', { name, exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name, exact: true })).toBeEnabled();
  }
});

test('renders processing library, AI provider and model options', async ({ page }) => {
  const processingLibrary = page.getByRole('combobox', { name: 'Processing library', exact: true });
  await expect(processingLibrary).toBeVisible();
  await expect(processingLibrary).toBeEnabled();
  await expect(processingLibrary.getByRole('option')).toHaveText(['Langchain']);
  await expect(processingLibrary).toHaveValue('Langchain');

  const aiProvider = page.getByRole('combobox', { name: 'AI Provider', exact: true });
  await expect(aiProvider).toBeVisible();
  await expect(aiProvider).toBeEnabled();
  await expect(aiProvider.getByRole('option')).toHaveText(['OpenAI', 'Ollama']);
  await expect(aiProvider).toHaveValue('OpenAI');

  const aiModel = page.getByRole('combobox', { name: 'AI Model', exact: true });
  await expect(aiModel).toBeVisible();
  await expect(aiModel).toBeEnabled();
  await expect(aiModel.getByRole('option')).toHaveText(['Test model']);
  await expect(aiModel).toHaveValue('test-model');
  await expect(page.locator('#ai-model-update-error')).toBeHidden();
  await expect(page.locator('#embedding-model-update-error')).toBeHidden();
});

test('loads embedding models on initial load and provider change', async ({ page }) => {
  const provider = page.getByRole('combobox', { name: 'AI Provider', exact: true });
  const embedding = page.getByRole('combobox', { name: 'Embedding model', exact: true });
  await expect(embedding).toBeEnabled();
  await expect(embedding.getByRole('option')).toHaveText(['text-embedding-3-small', 'text-embedding-3-large']);
  await embedding.selectOption('text-embedding-3-large');
  await provider.selectOption('Ollama');
  await expect(embedding.getByRole('option')).toHaveText(['nomic-embed-text']);
  await expect(embedding).toHaveValue('nomic-embed-text');
  await provider.selectOption('OpenAI');
  await expect(embedding).toHaveValue('text-embedding-3-small');
});

for (const savedModel of ['text-embedding-3-large', 'unavailable-model', '']) {
  test(`selects the saved embedding model or defaults to the first option (${savedModel || 'empty'})`, async ({ page }) => {
    const response = await page.request.post('/', {
      form: { ai_provider: 'OpenAI', embedding_model: savedModel },
    });
    await page.route('http://127.0.0.1:5000/', route => route.fulfill({ response }));
    await page.goto('/');
    const embedding = page.getByRole('combobox', { name: 'Embedding model', exact: true });
    await expect(embedding).toBeEnabled();
    await expect(embedding).toHaveValue(savedModel === 'text-embedding-3-large' ? savedModel : 'text-embedding-3-small');
  });
}

test('disables embedding models and reports a failed update', async ({ page }) => {
  await page.route('**/update_embedding_models?*', route => route.fulfill({ status: 500 }));
  await page.getByRole('combobox', { name: 'AI Provider', exact: true }).selectOption('Ollama');
  await expect(page.locator('#embedding-model-update-error')).toHaveText('Could not update embedding models. Try again.');
  await expect(page.getByRole('combobox', { name: 'Embedding model', exact: true })).toBeDisabled();
});

test('ignores a stale embedding model response after changing provider', async ({ page }) => {
  let releaseOldRequest!: () => void;
  const oldRequestReleased = new Promise<void>(resolve => { releaseOldRequest = resolve; });
  let oldRequestStarted!: () => void;
  const oldRequestSeen = new Promise<void>(resolve => { oldRequestStarted = resolve; });
  await page.route('**/update_embedding_models?*', async route => {
    if (new URL(route.request().url()).searchParams.get('ai_provider') === 'Ollama') {
      oldRequestStarted();
      await oldRequestReleased;
      await route.fulfill({ json: ['old-model'] });
    } else {
      await route.fulfill({ json: ['current-model'] });
    }
  });
  const provider = page.getByRole('combobox', { name: 'AI Provider', exact: true });
  const embedding = page.getByRole('combobox', { name: 'Embedding model', exact: true });
  await provider.selectOption('Ollama');
  await oldRequestSeen;
  await expect(embedding).toBeDisabled();
  await provider.selectOption('OpenAI');
  await expect(embedding).toHaveValue('current-model');
  const oldResponse = page.waitForResponse(response => response.url().includes('ai_provider=Ollama') &&
    response.url().includes('/update_embedding_models'));
  releaseOldRequest();
  await oldResponse;
  await expect(embedding.getByRole('option')).toHaveText(['current-model']);
});

test('renders the source document upload and guidance', async ({ page }) => {
  const upload = page.getByLabel('Upload a source document', { exact: true });
  await expect(upload).toBeVisible();
  await expect(upload).toBeEnabled();
  await expect(upload).toHaveAttribute('type', 'file');
  await expect(upload).toHaveAttribute('accept', '.pdf,.md,.docx');
  await expect(upload).toBeEmpty();
  await expect(page.getByText('The file must be a PDF, MD, or DOCX.')).toBeVisible();
  await expect(
    page.getByText('During the dev stage, this is a single file. TODO: add multiple document uploads'),
  ).toBeVisible();
});

for (const savedModel of ['second-model', 'unavailable-model', '']) {
  test(`selects the saved AI model or defaults to the first option (${savedModel || 'empty'})`, async ({ page }) => {
    await page.route('**/update_ai_models?*', async route => {
      await route.fulfill({
        json: [
          { name: 'First model', model: 'first-model' },
          { name: 'Second model', model: 'second-model' },
        ],
      });
    });

    const response = await page.request.post('/', {
      form: { ai_model: savedModel },
    });
    await page.route('http://127.0.0.1:5000/', route => route.fulfill({ response }));
    await page.goto('/');

    const aiModel = page.getByRole('combobox', { name: 'AI Model', exact: true });
    await expect(aiModel).toBeEnabled();
    await expect(aiModel).toHaveValue(savedModel === 'second-model' ? savedModel : 'first-model');
  });
}

test('renders the previous runs sidebar', async ({ page }) => {
  const sidebar = page.getByRole('complementary');
  await expect(sidebar.getByRole('heading', { name: 'Previous runs', level: 2 })).toBeVisible();
  await expect(
    sidebar.getByRole('navigation', { name: 'Previous runs' }).getByRole('link', { name: 'Run one' }),
  ).toBeVisible();
});
