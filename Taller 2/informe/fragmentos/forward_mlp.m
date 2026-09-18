function [y, cache] = forward_mlp(net, x, cfg)
    % Propaga la entrada x a través de todas las capas de la red.
    a{1} = x;
    L = numel(net.W);
    for k = 1:L
        netv{k} = net.W{k} * a{k} + net.b{k};
        if k == L
            a{k+1} = activation(netv{k}, cfg.act_output);
        else
            a{k+1} = activation(netv{k}, hidden_act(cfg, k));
        end
    end
    y = a{end};
    cache.a = a;
    cache.netv = netv;
end

function tipo = hidden_act(cfg, k)
    % Activación de la capa oculta k, una para todas o una por capa si act_hidden es celda.
    if iscell(cfg.act_hidden), tipo = cfg.act_hidden{k}; else, tipo = cfg.act_hidden; end
end
