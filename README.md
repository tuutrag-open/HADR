# Citation & Link Guide

This project uses a custom "Preview System" (located in `js/preview.js`) that displays context popups when users hover over citations, technical terms, or external links.

## Internal Citations (Standard)
This is the primary method for this paper. Use this for bibliography references, footnotes, or appendices.

### Step A: Add the Reference
At the bottom of `index.html`, inside the References list, add the citation. 

**Crucial:** You must give the `<li>` a unique `id`.

```html
<div class="references">
    <h3>References</h3>
    <ul>
        <li id="ref-vaswani">
            Vaswani, A., et al. (2017). <em>Attention is All You Need.</em> Advances in Neural Information Processing Systems.
        </li>
        
        <li id="ref-bert">
            Devlin, J., et al. (2018). <em>BERT: Pre-training of Deep Bidirectional Transformers.</em> arXiv preprint.
        </li>
    </ul>
</div>
```

### Step B: Link in Text

In paragraphs, link to that ID using href="#id".
```html
<p>
    Transformer models have revolutionized NLP <a href="#ref-vaswani">[1]</a>.
    Unlike previous approaches, BERT <a href="#ref-bert">[2]</a> utilizes bidirectional training.
</p>
```

## External Links (Manual Preview)

If you want to link to a GitHub repo, a tool, or a website that isn't Wikipedia, you can manually write the popup text using data- attributes.

__data-title__: The header text in the popup.

__data-preview__: The body text (keep it short, ~2 sentences).

```html
<p>
    We utilized 
    <a href="[https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain)" 
       data-title="LangChain" 
       data-preview="A framework for developing applications powered by language models.">
       LangChain
    </a> 
    for the orchestration layer.
</p>
```

## Wikipedia Links (Automatic)

No special formatting is required. Any link pointing to en.wikipedia.org will automatically fetch the article summary and thumbnail image.

```html
<p>
    The system relies heavily on <a href="[https://en.wikipedia.org/wiki/Word_embedding](https://en.wikipedia.org/wiki/Word_embedding)">Vector Embeddings</a>.
</p>
```