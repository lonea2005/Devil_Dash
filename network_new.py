import torch
import torch.nn as nn
import math
from utils import *
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, head_num):
        super().__init__()
        self.d_model = d_model
        self.head_num = head_num
        self.head_dim = d_model // head_num

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.fc = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(0.2)

    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        attn_weights = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if mask is not None:
            attn_weights = attn_weights.masked_fill(mask == 0, -1e9)
        
        attn_weights = F.softmax(attn_weights, dim=-1)
        attn_weights = self.dropout(attn_weights)
        output = torch.matmul(attn_weights, V)
        return output, attn_weights
    
    def forward(self, Q, K, V, src_padding_mask=None, future_mask=None):
        batch_size, seq_len = Q.size(0), Q.size(1)
        
        # Apply linear transformations and reshape for multi-head attention
        Q = self.W_q(Q).view(batch_size, seq_len, self.head_num, self.head_dim).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.head_num, self.head_dim).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.head_num, self.head_dim).transpose(1, 2)

        attn_output, attn_weights = self.scaled_dot_product_attention(Q, K, V, mask=src_padding_mask)
        
        # Concatenate heads and apply final linear transformation
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.fc(attn_output), attn_weights


class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model, dim_feedforward, nhead, dropout):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, nhead)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, d_model)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x, src_padding_mask):
        # Self-attention with residual connection and layer norm
        attn_output, _ = self.self_attn(x, x, x, src_padding_mask)
        x = self.norm1(x + attn_output)
        
        # Feed-forward with residual connection and layer norm
        ff_output = self.feed_forward(x)
        return self.norm2(x + ff_output)


class TransformerDecoderLayer(nn.Module):
    def __init__(self, d_model, dim_feedforward, nhead, dropout):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, nhead)
        self.cross_attn = MultiHeadAttention(d_model, nhead)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, d_model)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)

    def forward(self, x, enc_output, src_padding_mask=None, tgt_padding_mask=None, tgt_future_mask=None):
        # Combine masks if both exist
        combined_mask = tgt_future_mask & tgt_padding_mask if tgt_future_mask is not None and tgt_padding_mask is not None else tgt_future_mask
        
        # Self-attention with residual connection and layer norm
        self_attn_output, _ = self.self_attn(x, x, x, combined_mask)
        x = self.norm1(x + self_attn_output)

        # Cross-attention with residual connection and layer norm
        cross_attn_output, _ = self.cross_attn(x, enc_output, enc_output, src_padding_mask)
        x = self.norm2(x + cross_attn_output)

        # Feed-forward with residual connection and layer norm
        ff_output = self.feed_forward(x)
        return self.norm3(x + ff_output)


class Transformer(nn.Module): 
    def __init__(self, d_model, num_heads, num_encoder_layers, num_decoder_layers, d_ff, dropout, tgt_vocab_size):
        super().__init__()
        self.encoder_layers = nn.ModuleList([
            TransformerEncoderLayer(d_model, d_ff, num_heads, dropout) 
            for _ in range(num_encoder_layers)
        ])
        self.decoder_layers = nn.ModuleList([
            TransformerDecoderLayer(d_model, d_ff, num_heads, dropout) 
            for _ in range(num_decoder_layers)
        ])
        self.generator = nn.Linear(d_model, tgt_vocab_size)
        self.positional_encoding = PositionalEncoding(d_model, dropout)

    def forward(self, src_embeded, tgt_embeded, src_padding_mask, tgt_padding_mask, tgt_future_mask):
        enc_output = self.encode(src_embeded, src_padding_mask)
        return self.decode(tgt_embeded, enc_output, src_padding_mask, tgt_padding_mask, tgt_future_mask)

    def encode(self, src_embeded, src_padding_mask=None): 
        for layer in self.encoder_layers:
            src_embeded = layer(src_embeded, src_padding_mask)
        return src_embeded
        
    def decode(self, tgt_embeded, enc_output, src_padding_mask=None, tgt_padding_mask=None, tgt_future_mask=None):
        for layer in self.decoder_layers:
            tgt_embeded = layer(tgt_embeded, enc_output, src_padding_mask, tgt_padding_mask, tgt_future_mask)
        return tgt_embeded


class PositionalEncoding(nn.Module):
    def __init__(self, emb_size, dropout=0.2, maxlen=5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(0, maxlen).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, emb_size, 2) * (-math.log(10000.0) / emb_size))
        pe = torch.zeros(maxlen, emb_size)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, token_embedding):
        token_embedding = token_embedding + self.pe[:, :token_embedding.size(1), :].detach()
        return self.dropout(token_embedding)
    

class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size, emb_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_size)
        self.emb_size = emb_size
        self.vocab_size = vocab_size

    def forward(self, tokens):
        return self.embedding(tokens) * math.sqrt(self.emb_size)


class Seq2SeqNetwork(nn.Module):
    def __init__(self, 
                 num_encoder_layers,
                 num_decoder_layers,
                 emb_size,
                 nhead,
                 src_vocab_size,
                 tgt_vocab_size,
                 dim_feedforward,
                 dropout=0.1, 
                 device='cpu'):
        super().__init__()
        self.device = device
        self.transformer = Transformer(
            d_model=emb_size,
            num_heads=nhead,
            num_encoder_layers=num_encoder_layers,
            num_decoder_layers=num_decoder_layers,
            d_ff=dim_feedforward,
            dropout=dropout,
            tgt_vocab_size=tgt_vocab_size
        )
        self.generator = nn.Linear(emb_size, tgt_vocab_size)
        self.src_tok_emb = TokenEmbedding(src_vocab_size, emb_size)
        self.tgt_tok_emb = TokenEmbedding(tgt_vocab_size, emb_size)
        self.positional_encoding = PositionalEncoding(emb_size, dropout=dropout)

    def _embed_tokens(self, tokens, embedding_layer):
        """Helper method to embed and add positional encoding"""
        return self.positional_encoding(embedding_layer(tokens.long()))

    def forward(self, src, tgt, tgt_future_mask=None, src_padding_mask=None, tgt_padding_mask=None):
        src_emb = self._embed_tokens(src, self.src_tok_emb)
        tgt_emb = self._embed_tokens(tgt, self.tgt_tok_emb)

        outs = self.transformer(src_emb, tgt_emb, src_padding_mask, tgt_padding_mask, tgt_future_mask)
        return self.generator(outs)

    def encode(self, src, src_padding_mask=None):
        return self.transformer.encode(self._embed_tokens(src, self.src_tok_emb), src_padding_mask)

    def decode(self, tgt, memory, src_padding_mask=None, tgt_padding_mask=None, tgt_future_mask=None):
        return self.transformer.decode(self._embed_tokens(tgt, self.tgt_tok_emb), memory, src_padding_mask, tgt_padding_mask, tgt_future_mask)


def generate_square_subsequent_mask(size):
    """Generate causal mask for decoder self-attention"""
    return torch.tril(torch.ones((size, size), device=DEVICE), diagonal=0).bool()


def greedy_decode(model, src, src_mask, max_len, start_symbol):
    """Greedy decoding for inference"""
    src = src.to(DEVICE)
    src_mask = src_mask.to(DEVICE)
    memory = model.encode(src, src_padding_mask=src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type(torch.long).to(DEVICE)
    
    for i in range(max_len - 1):
        memory = memory.to(DEVICE)
        tgt_padding_mask = torch.ones(1, ys.size(1)).type(torch.bool).to(DEVICE)
        tgt_mask = generate_square_subsequent_mask(ys.size(1)).to(DEVICE)
        
        out = model.decode(ys, memory, src_padding_mask=src_mask, 
                          tgt_padding_mask=tgt_padding_mask, tgt_future_mask=tgt_mask)
        prob = model.generator(out[-1, :])
        _, next_word = torch.max(prob, dim=1)
        next_word = next_word.item()

        ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=1)
        if next_word == EOS_IDX:
            break
    return ys


def translate(model: torch.nn.Module, src_sentence: str, input_tokenizer, output_tokenizer):
    """Translate a sentence from source to target language"""
    model.eval()
    sentence = torch.tensor(input_tokenizer.encode(src_sentence)).view(1, -1).to(DEVICE)
    num_tokens = sentence.shape[1]
    
    src_mask = torch.ones((1, num_tokens)).type(torch.bool).to(DEVICE)
    tgt_tokens = greedy_decode(model, sentence, src_mask, max_len=num_tokens + 5, start_symbol=BOS_IDX).flatten()
    
    return output_tokenizer.decode(tgt_tokens, skip_special_tokens=True)


def load_model(MODEL_PATH=None): 
    """Load the transformer model with specified configuration"""
    EMB_SIZE = 512
    NHEAD = 8
    FFN_HID_DIM = 512
    NUM_ENCODER_LAYERS = 2
    NUM_DECODER_LAYERS = 2
    SRC_VOCAB_SIZE = tokenizer_chinese().vocab_size
    TGT_VOCAB_SIZE = tokenizer_english().vocab_size

    model = Seq2SeqNetwork(NUM_ENCODER_LAYERS, NUM_DECODER_LAYERS, EMB_SIZE, NHEAD, 
                          SRC_VOCAB_SIZE, TGT_VOCAB_SIZE, FFN_HID_DIM, device=DEVICE)
    if MODEL_PATH is not None: 
        model.load_state_dict(torch.load(MODEL_PATH))
    return model