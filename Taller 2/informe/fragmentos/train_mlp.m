function [net, hist] = train_mlp(Xtr, Dtr, Xva, Dva, cfg)
    % Mismo ciclo de la sección 8, con error de validación por época y parada
    % temprana cuando la validación lleva cfg.patience épocas sin mejorar.
    rng(cfg.seed);
    net = init_mlp(cfg);
    hist.train = zeros(cfg.max_epochs, 1);  hist.val = hist.train;
    mejor = Inf;  sin_mejora = 0;  mejor_net = net;
    for epoch = 1:cfg.max_epochs
        for p = randperm(size(Xtr, 1))
            [~, cache] = forward_mlp(net, Xtr(p, :)', cfg);
            net = backward_mlp(net, cache, Xtr(p, :)', Dtr(p, :)', cfg);
        end
        hist.train(epoch) = mse_mlp(net, Xtr, Dtr, cfg);
        if ~isempty(Xva), hist.val(epoch) = mse_mlp(net, Xva, Dva, cfg); end
        if hist.train(epoch) <= cfg.target_error, break; end
        if cfg.patience > 0 && ~isempty(Xva)
            if hist.val(epoch) < mejor
                mejor = hist.val(epoch);  sin_mejora = 0;  mejor_net = net;
            else
                sin_mejora = sin_mejora + 1;
                if sin_mejora >= cfg.patience, net = mejor_net; break; end
            end
        end
    end
    hist.train = hist.train(1:epoch);  hist.val = hist.val(1:epoch);  hist.epochs = epoch;
end
