package br.com.igoorj.courses.service;

import br.com.igoorj.courses.dto.CourseRequest;
import br.com.igoorj.courses.entity.Course;
import br.com.igoorj.courses.repository.CourseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CourseService {

    private final CourseRepository courseRepository;

    public List<Course> findAll() {
        return courseRepository.findAll();
    }

    public Course findById(Long id) {
        return courseRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Course not found"));
    }

    public Course create(CourseRequest request) {
        var course = new Course();
        course.setName(request.name());
        course.setDescription(request.description());
        return courseRepository.save(course);
    }

    public Course update(Long id, CourseRequest request) {
        Course course = findById(id);
        course.setName(request.name());
        course.setDescription(request.description());
        return courseRepository.save(course);
    }

    public List<Course> findByName(String name) {
        return courseRepository.findByNameContainingIgnoreCase(name);
    }

    public void delete(Long id) {
        findById(id);
        courseRepository.deleteById(id);
    }
}
