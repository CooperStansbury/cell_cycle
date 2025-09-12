# Saved Model

TensorFlow SavedModel exported from DeepCycle, suitable for loading with `tf.saved_model.load` for downstream inference.

- `saved_model.pb` – model graph definition.
- `variables/` – trained weights.

Load the model in Python with:

```python
import tensorflow as tf
model = tf.saved_model.load('path/to/model')
```

Use the exported signatures to perform inference on new expression matrices.

