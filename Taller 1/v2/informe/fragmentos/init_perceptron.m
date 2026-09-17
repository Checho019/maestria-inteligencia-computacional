function [W, b] = init_perceptron(cfg)
    % Inicializa pesos y sesgo con valores aleatorios pequeños.
    W = randn(1, cfg.n_inputs) * cfg.init_scale;
    b = randn(1) * cfg.init_scale;
end
