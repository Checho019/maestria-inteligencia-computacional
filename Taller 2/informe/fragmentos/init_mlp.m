function net = init_mlp(cfg)
    % Inicializa pesos y sesgos de todas las capas en la estructura `net`.
    net = struct();
    net.W = {};
    net.b = {};
    net.dW_prev = {};
    net.db_prev = {};
    layer_sizes = [cfg.n_inputs, cfg.hidden_layers, cfg.n_outputs];
    escala = 0.5;  if isfield(cfg, 'init_scale'), escala = cfg.init_scale; end
    for k = 1:numel(layer_sizes) - 1
        net.W{k} = randn(layer_sizes(k+1), layer_sizes(k)) * escala;
        net.b{k} = zeros(layer_sizes(k+1), 1);
        net.dW_prev{k} = zeros(size(net.W{k}));
        net.db_prev{k} = zeros(size(net.b{k}));
    end
end
