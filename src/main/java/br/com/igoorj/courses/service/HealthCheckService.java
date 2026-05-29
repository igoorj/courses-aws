package br.com.igoorj.courses.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class HealthCheckService {

    public String ok() {
        return "OK";
    }
}
