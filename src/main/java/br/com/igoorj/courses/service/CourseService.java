package br.com.igoorj.courses.service;

import br.com.igoorj.courses.dto.CourseRequest;
import br.com.igoorj.courses.entity.Course;
import br.com.igoorj.courses.repository.CourseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CourseService {

    private final CourseRepository courseRepository;

    public List<Course> findAll() {
        return courseRepository.findAll();
    }

    public Course create(CourseRequest request) {
        var course = new Course();
        course.setName(request.name());
        course.setDescription(request.description());
        return courseRepository.save(course);
    }
}
