# Datasets, examples, code and results

Read when the paper has datasets, benchmarks or code, or the guide prints code.

## One example, end to end

For empirical and systems papers, follow one real item from a dataset the paper uses through the method: the input as the model receives it, what the model computes, how the output is scored, and, for a training example, the loss and the update. Use the paper's own numbers where it gives them, and introduce any other value as an example in the sentence ("for example, if a word averaged 1.3 pieces").

## Datasets

Give each dataset one real item, quoted from the paper (its prompt-format appendix when it has one), shortened with "..." and tagged with its figure and a `[p. N]` marker. When the paper prints none, say so, and either use the dataset's own published example, naming its source in the item's heading ("from the wmt/wmt14 dataset on Hugging Face"), or describe the format.

## Code

- Each snippet's text says what it shows and what it does not show. A gradient read at the input includes every path through the model; it does not isolate one path of the math.
- A comparison changes one thing: the same seed and weights, with only the setting under test changed (for example, a forget-gate bias of 0 against 1).
- When you set a library parameter, set every parameter the library combines with it. PyTorch's LSTM adds `bias_ih` and `bias_hh`, so setting one leaves the sum random.
- A number that comes from running code is printed by a snippet in the guide. Never quote a value from a side run the reader cannot see.

## Results

Judge each score against its chance level. For empirical papers, the scoreboard (`scripts/scoreboard.py`) rates every benchmark by gap closed: (score − floor) ÷ (comparison − floor), where the floor is the chance level, or 0 for open-answer metrics. Label it as the guide's measure.
