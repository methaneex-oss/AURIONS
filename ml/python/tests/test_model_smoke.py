from pathlib import Path

import torch

from aurions_ml.model import ByteTokenizer, DecoderConfig, DecoderOnlyTransformer
from aurions_ml.smoke_train import run_smoke_training


def test_byte_tokenizer_round_trips_multilingual_utf8():
    tokenizer = ByteTokenizer()
    text = "Hello, 你好, مرحبا, Ẹ káàbọ̀"
    assert tokenizer.decode(tokenizer.encode(text)) == text


def test_transformer_is_causal():
    torch.manual_seed(7)
    model = DecoderOnlyTransformer(
        DecoderConfig(context_length=8, width=16, heads=4, layers=1, feed_forward_width=32)
    ).eval()
    first = torch.tensor([[1, 2, 3, 4]])
    changed_future = torch.tensor([[1, 2, 99, 100]])
    with torch.no_grad():
        a = model(first)
        b = model(changed_future)
    assert torch.allclose(a[:, :2], b[:, :2], atol=1e-6, rtol=0.0)


def test_random_initialized_model_trains_and_checkpoint_reloads(tmp_path: Path):
    result = run_smoke_training(tmp_path / "baseline.pt", steps=60)
    assert result["parameters"] > 10_000
    assert result["final_heldout_loss"] < result["initial_heldout_loss"]
    assert result["max_reload_logit_delta"] == 0.0
    assert result["artifact_kind"] == "synthetic-training-smoke-only"
    assert result["candidate_status"] == "quarantined"
    assert result["activation_eligible"] is False


def test_training_checkpoint_resumes_to_same_weights(tmp_path: Path):
    continuous = run_smoke_training(tmp_path / "continuous.pt", steps=20)
    run_smoke_training(tmp_path / "partial.pt", steps=10)
    resumed = run_smoke_training(
        tmp_path / "resumed.pt", steps=20, resume_from=tmp_path / "partial.pt"
    )
    full_state = torch.load(tmp_path / "continuous.pt", map_location="cpu", weights_only=True)
    resumed_state = torch.load(tmp_path / "resumed.pt", map_location="cpu", weights_only=True)
    for name, tensor in full_state["state_dict"].items():
        assert torch.equal(tensor, resumed_state["state_dict"][name]), name
    assert resumed["final_heldout_loss"] == continuous["final_heldout_loss"]


def test_resume_rejects_different_seed(tmp_path: Path):
    run_smoke_training(tmp_path / "source.pt", steps=5, seed=7)
    try:
        run_smoke_training(
            tmp_path / "rejected.pt", steps=10, seed=8, resume_from=tmp_path / "source.pt"
        )
    except ValueError as error:
        assert "seed" in str(error)
    else:
        raise AssertionError("incompatible checkpoint was accepted")
