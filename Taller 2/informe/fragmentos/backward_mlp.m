function net = backward_mlp(net, cache, x, d, cfg)
    % Calcula los delta de cada capa y actualiza los pesos (ver fórmulas
    % de la Sección 1 de este mismo script).
    L = numel(net.W);
    delta = cell(1, L);
    delta{L} = (d - cache.a{L+1}) .* activation_deriv(cache.netv{L}, cfg.act_output);
    for k = L-1:-1:1
        delta{k} = (net.W{k+1}' * delta{k+1}) .* activation_deriv(cache.netv{k}, hidden_act(cfg, k));
    end
    for k = 1:L
        dW = cfg.eta * delta{k} * cache.a{k}' + cfg.momentum * net.dW_prev{k};
        db = cfg.eta * delta{k} + cfg.momentum * net.db_prev{k};
        net.W{k} = net.W{k} + dW;
        net.b{k} = net.b{k} + db;
        net.dW_prev{k} = dW;
        net.db_prev{k} = db;
    end
end
