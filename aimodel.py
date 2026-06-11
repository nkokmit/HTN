import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# Thiết lập thiết bị chạy (Sử dụng GPU nếu có, không thì CPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Đang sử dụng thiết bị: {device}")

# ==========================================
# 1. TIỀN XỬ LÝ DỮ LIỆU (DATA PREPARATION)
# ==========================================
df = pd.read_csv('data_user500.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(by=['user_id', 'timestamp'])

le = LabelEncoder()
# Cộng 1 để chừa số 0 làm giá trị Padding
df['action_encoded'] = le.fit_transform(df['action']) + 1 
num_classes = len(le.classes_) + 1 

sequences = []
targets = []

for _, group in df.groupby('user_id'):
    seq = group['action_encoded'].tolist()
    if len(seq) > 1:
        for i in range(1, len(seq)):
            sequences.append(seq[:i])
            targets.append(seq[i])

max_len = 10
# Padding chuỗi bằng Numpy (Pre-padding: chèn 0 vào đầu)
X_padded = np.zeros((len(sequences), max_len), dtype=np.int64)
for i, seq in enumerate(sequences):
    length = min(len(seq), max_len)
    X_padded[i, -length:] = seq[-length:]

y = np.array(targets, dtype=np.int64)

# Chia tập Train/Test (80% Train, 20% Test)
split = int(0.8 * len(X_padded))
X_train, X_test = X_padded[:split], X_padded[split:]
y_train, y_test = y[:split], y[split:]


# ==========================================
# 2. TẠO DATALOADER TRONG PYTORCH
# ==========================================
batch_size = 32

train_dataset = TensorDataset(torch.tensor(X_train), torch.tensor(y_train))
test_dataset = TensorDataset(torch.tensor(X_test), torch.tensor(y_test))

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)


# ==========================================
# 3. ĐỊNH NGHĨA KIẾN TRÚC MÔ HÌNH (PYTORCH)
# ==========================================
class ActionPredictor(nn.Module):
    def __init__(self, model_type, num_classes, embed_dim=8, hidden_dim=16):
        super(ActionPredictor, self).__init__()
        self.model_type = model_type
        
        # Tầng Embedding (padding_idx=0 giúp bỏ qua các giá trị 0)
        self.embedding = nn.Embedding(num_classes, embed_dim, padding_idx=0)
        
        # Tầng Recurrent
        if model_type == 'RNN':
            self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)
        elif model_type == 'LSTM':
            self.rnn = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        elif model_type == 'biLSTM':
            self.rnn = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
            
        # Tầng Output phân loại
        # Nếu là biLSTM, kích thước hidden state nhân đôi (forward + backward)
        out_dim = hidden_dim * 2 if model_type == 'biLSTM' else hidden_dim
        self.fc = nn.Linear(out_dim, num_classes)
        
    def forward(self, x):
        embeds = self.embedding(x)
        out, _ = self.rnn(embeds)
        # Chỉ lấy output ở bước thời gian (time step) cuối cùng của mỗi chuỗi
        out = out[:, -1, :] 
        logits = self.fc(out) 
        # Không cần Softmax ở đây vì hàm CrossEntropyLoss của PyTorch đã tự động bao gồm nó
        return logits


# ==========================================
# 4. HÀM HUẤN LUYỆN VÀ ĐÁNH GIÁ (TRAINING LOOP)
# ==========================================
def train_and_evaluate(model, train_loader, test_loader, epochs=15):
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters())
    
    history = {'train_loss': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        # Đánh giá trên tập Validation
        model.eval()
        val_loss, correct, total = 0, 0, 0
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                val_loss += loss.item()
                
                # Lấy class có xác suất cao nhất
                _, predicted = torch.max(outputs.data, 1)
                total += y_batch.size(0)
                correct += (predicted == y_batch).sum().item()
                
        epoch_val_acc = correct / total
        history['train_loss'].append(total_loss / len(train_loader))
        history['val_loss'].append(val_loss / len(test_loader))
        history['val_acc'].append(epoch_val_acc)
        
        # Chỉ in kết quả ở một số epoch để console bớt dài
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch [{epoch+1}/{epochs}] - Val Loss: {val_loss/len(test_loader):.4f} - Val Acc: {epoch_val_acc:.4f}")
            
    return history


# Khởi tạo 3 mô hình
models = {
    'RNN': ActionPredictor('RNN', num_classes),
    'LSTM': ActionPredictor('LSTM', num_classes),
    'biLSTM': ActionPredictor('biLSTM', num_classes)
}

# Tiến hành huấn luyện
all_history = {}
for name, model in models.items():
    print(f"\n=== Đang huấn luyện mô hình {name} ===")
    all_history[name] = train_and_evaluate(model, train_loader, test_loader, epochs=15)


# ==========================================
# 5. TRỰC QUAN HÓA KẾT QUẢ (VISUALIZATION)
# ==========================================
plt.figure(figsize=(12, 5))

# Plot Validation Accuracy
plt.subplot(1, 2, 1)
for name, hist in all_history.items():
    plt.plot(hist['val_acc'], label=f'{name} (Val Acc)')
plt.title('Độ chính xác (Validation Accuracy) - PyTorch')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.grid(True)
plt.legend()

# Plot Validation Loss
plt.subplot(1, 2, 2)
for name, hist in all_history.items():
    plt.plot(hist['val_loss'], label=f'{name} (Val Loss)')
plt.title('Hàm mất mát (Validation Loss) - PyTorch')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig('pytorch_model_comparison.png')
plt.show()

# Đánh giá mô hình tốt nhất
print("\n" + "="*40)
print("KẾT QUẢ ĐÁNH GIÁ (EPOCH CUỐI CÙNG)")
print("="*40)
for name in models:
    final_val_acc = all_history[name]['val_acc'][-1]
    print(f"{name} Validation Accuracy: {final_val_acc:.4f}")

best_model_name = max(all_history, key=lambda k: all_history[k]['val_acc'][-1])
print(f"\n=> MÔ HÌNH TỐT NHẤT (model_best): {best_model_name}")