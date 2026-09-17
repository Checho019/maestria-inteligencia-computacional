function [Xtr, Dtr, Xte, Dte] = split_dataset(X, D, train_ratio, seed)
    % Divide (X, D) en un subconjunto de entrenamiento y uno de prueba,
    % respetando la proporción train_ratio (p. ej. 0.7 = 70% entrenamiento).
    rng(seed);
    n = size(X, 1);
    idx = randperm(n);
    n_train = round(train_ratio * n);
    idx_train = idx(1:n_train);
    idx_test  = idx(n_train+1:end);
    Xtr = X(idx_train, :); Dtr = D(idx_train, :);
    Xte = X(idx_test, :);  Dte = D(idx_test, :);
end
